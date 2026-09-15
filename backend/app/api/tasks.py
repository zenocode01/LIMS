from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_role
from ..models.entrust import Entrustment
from ..models.sample import Sample, SampleEvent
from ..models.standard import StandardItem
from ..models.task import TASK_TRANSITIONS, Task
from ..models.user import User
from ..numbering.service import no_task
from ..schemas.task import TaskOut

# 任务权限（设计规格 §5 推导）: 所有人可查看（含客户名）;
# 工程师执行测试（开始/完成）, 管理全量 + 打回重测
READER = Depends(require_role("business", "engineer", "admin"))
EXECUTOR = Depends(require_role("engineer", "admin"))
ADMIN = Depends(require_role("admin"))

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class RetestIn(BaseModel):
    reason: str | None = None


def _get_or_404(db: Session, task_id: int) -> Task:
    t = db.get(Task, task_id)
    if t is None:
        raise HTTPException(404, "任务不存在")
    return t


def _set_status(t: Task, to: str, **fields) -> None:
    if to not in TASK_TRANSITIONS.get(t.status, ()):
        raise HTTPException(409, f"任务当前状态「{t.status}」不允许迁移到「{to}」")
    t.status = to
    for k, v in fields.items():
        setattr(t, k, v)


def _on_testing(t: Task) -> None:
    """开测钩子: 样品 已登记→在测（留痕）; 委托单 已确认→测试中。"""
    s = t.sample
    if s and s.status == "registered":
        s.events.append(SampleEvent(from_status="registered", to_status="in_test", operator="system"))
        s.status = "in_test"
    e = t.entrustment
    if e and e.status == "confirmed":
        e.status = "testing"


@router.get("", response_model=list[TaskOut], dependencies=[READER])
def list_tasks(
    q: str | None = Query(default=None, description="任务号/样品号/项目名/委托单号模糊搜索"),
    status: str | None = Query(default=None, description="状态过滤"),
    category: str | None = Query(default=None, description="类别过滤 EMI/EMS"),
    entrustment_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if category:
        query = query.filter(Task.category == category)
    if entrustment_id:
        query = query.filter(Task.entrustment_id == entrustment_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Task.code.like(like),
                Task.entrustment.has(Entrustment.code.like(like)),
                Task.sample.has(Sample.code.like(like)),
                Task.item.has(StandardItem.name.like(like)),
            )
        )
    return [TaskOut.from_orm(x) for x in query.order_by(Task.id.desc()).limit(limit).all()]


@router.get("/{task_id}", response_model=TaskOut, dependencies=[READER])
def get_task(task_id: int, db: Session = Depends(get_db)):
    return TaskOut.from_orm(_get_or_404(db, task_id))


@router.post("/{task_id}/start", response_model=TaskOut, dependencies=[EXECUTOR])
def start_task(task_id: int, db: Session = Depends(get_db)):
    t = _get_or_404(db, task_id)
    # 已完成的任务走 /retest（管理打回）, 此处仅 未排程/已排程 → 测试中
    if t.status not in ("unscheduled", "scheduled"):
        raise HTTPException(409, f"任务当前状态「{t.status}」不可开测")
    _set_status(t, "testing", started_at=datetime.utcnow())
    _on_testing(t)
    db.commit()
    db.refresh(t)
    return TaskOut.from_orm(t)


@router.post("/{task_id}/complete", response_model=TaskOut, dependencies=[EXECUTOR])
def complete_task(task_id: int, db: Session = Depends(get_db)):
    t = _get_or_404(db, task_id)
    _set_status(t, "completed", completed_at=datetime.utcnow())
    db.commit()
    db.refresh(t)
    return TaskOut.from_orm(t)


@router.post("/{task_id}/retest", response_model=TaskOut, dependencies=[ADMIN])
def retest_task(task_id: int, payload: RetestIn, db: Session = Depends(get_db)):
    """打回重测（设计规格 §3）: 完成→测试中, 管理触发、留原因。"""
    t = _get_or_404(db, task_id)
    if t.status != "completed":
        raise HTTPException(409, f"任务当前状态「{t.status}」不可打回（需已完成）")
    _set_status(
        t,
        "testing",
        started_at=datetime.utcnow(),
        completed_at=None,
        retest_reason=payload.reason,
    )
    db.commit()
    db.refresh(t)
    return TaskOut.from_orm(t)


def generate_tasks_for_entrustment(db: Session, e: Entrustment) -> int:
    """确认委托钩子（设计规格 §3）: 按 标准项目 × 样品 自动生成测试任务。

    项目来源: 来源报价单明细挂的标准项目引用; 样品来源: 该委托单下已登记样品。
    返回生成的任务数（0 = 无标准项目引用或无样品, 属合法状态）。
    """
    item_ids: list[int] = []
    if e.source_quote is not None:
        for it in e.source_quote.items:
            if it.standard_item_id is not None:
                item_ids.append(it.standard_item_id)
    samples = (
        db.query(Sample).filter(Sample.entrustment_id == e.id).all()
    )
    count = 0
    for sample in samples:
        for item_id in item_ids:
            item = db.get(StandardItem, item_id)
            if item is None:
                continue
            db.add(
                Task(
                    code=no_task(db),
                    entrustment_id=e.id,
                    sample_id=sample.id,
                    item_id=item.id,
                    category=item.category,
                )
            )
            count += 1
    db.flush()
    return count
