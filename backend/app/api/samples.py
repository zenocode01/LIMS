from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_role
from ..models.entrust import Entrustment
from ..models.sample import SAMPLE_TRANSITIONS, Sample, SampleEvent
from ..models.user import User
from ..numbering.service import no_sample
from ..schemas.sample import SampleIn, SampleOut, TransitionIn

# 权限（设计规格 §5）: 业务=登记/流转, 工程师=查看, 管理=全量
READER = Depends(require_role("business", "engineer", "admin"))
WRITER = Depends(require_role("business", "admin"))

router = APIRouter(prefix="/api/samples", tags=["samples"])


def _get_or_404(db: Session, sample_id: int) -> Sample:
    s = db.get(Sample, sample_id)
    if s is None:
        raise HTTPException(404, "样品不存在")
    return s


def _transition(s: Sample, to: str, operator: str | None, note: str | None) -> None:
    """状态机守卫 + 流转留痕。"""
    if to not in SAMPLE_TRANSITIONS.get(s.status, ()):
        raise HTTPException(409, f"样品当前状态「{s.status}」不允许迁移到「{to}」")
    s.events.append(
        SampleEvent(from_status=s.status, to_status=to, operator=operator, note=note)
    )
    s.status = to


@router.get("", response_model=list[SampleOut], dependencies=[READER])
def list_samples(
    q: str | None = Query(default=None, description="编号/名称型号/外部单号/委托单号模糊搜索"),
    status: str | None = Query(default=None, description="状态过滤"),
    entrustment_id: int | None = Query(default=None, description="按委托单过滤"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Sample)
    if status:
        query = query.filter(Sample.status == status)
    if entrustment_id:
        query = query.filter(Sample.entrustment_id == entrustment_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Sample.code.like(like),
                Sample.name_model.like(like),
                Sample.external_no.like(like),
                Sample.entrustment.has(Entrustment.code.like(like)),
            )
        )
    return [SampleOut.from_orm(x) for x in query.order_by(Sample.id.desc()).limit(limit).all()]


@router.get("/{sample_id}", response_model=SampleOut, dependencies=[READER])
def get_sample(sample_id: int, db: Session = Depends(get_db)):
    return SampleOut.from_orm(_get_or_404(db, sample_id))


@router.post("", response_model=SampleOut, status_code=201, dependencies=[WRITER])
def create_sample(
    payload: SampleIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Entrustment, payload.entrustment_id) is None:
        raise HTTPException(404, "委托单不存在")
    s = Sample(
        code=no_sample(db),
        entrustment_id=payload.entrustment_id,
        name_model=payload.name_model,
        appearance=payload.appearance,
        external_no=payload.external_no,
        created_by=user.username,
    )
    s.events.append(
        SampleEvent(from_status=None, to_status="registered", operator=user.username)
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return SampleOut.from_orm(s)


@router.post("/{sample_id}/transition", response_model=SampleOut, dependencies=[WRITER])
def transition_sample(
    sample_id: int,
    payload: TransitionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = _get_or_404(db, sample_id)
    _transition(s, payload.to, user.username, payload.note)
    db.commit()
    db.refresh(s)
    return SampleOut.from_orm(s)
