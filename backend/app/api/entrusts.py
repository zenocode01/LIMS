from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_role
from ..models.customer import Customer
from ..models.entrust import ENTRUST_TRANSITIONS, Entrustment
from ..models.quote import QUOTE_TRANSITIONS, Quotation
from ..models.user import User
from ..numbering.service import no_entrustment
from ..schemas.entrust import EntrustIn, EntrustOut, EntrustUpdate, TerminateIn

# 权限（设计规格 §5）: 业务=创建/编辑/确认, 工程师=查看, 管理=全量+终止
READER = Depends(require_role("business", "engineer", "admin"))
WRITER = Depends(require_role("business", "admin"))
ADMIN = Depends(require_role("admin"))

router = APIRouter(prefix="/api/entrustments", tags=["entrustments"])


def _get_or_404(db: Session, entrust_id: int) -> Entrustment:
    e = db.get(Entrustment, entrust_id)
    if e is None:
        raise HTTPException(404, "委托单不存在")
    return e


def _set_status(e: Entrustment, to: str, **fields) -> None:
    """状态机守卫：非法迁移 409。"""
    if to not in ENTRUST_TRANSITIONS.get(e.status, ()):
        raise HTTPException(409, f"委托单当前状态「{e.status}」不允许迁移到「{to}」")
    e.status = to
    for k, v in fields.items():
        setattr(e, k, v)


def _quote_items_brief(quote: Quotation) -> str:
    """报价明细摘要，作为转入委托单的初始「委托要求」。"""
    return "\n".join(f"{i.item_name} x{i.qty}" for i in quote.items) or "（报价无明细）"


@router.get("", response_model=list[EntrustOut], dependencies=[READER])
def list_entrustments(
    q: str | None = Query(default=None, description="编号/客户名称/外部单号模糊搜索"),
    status: str | None = Query(default=None, description="状态过滤"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Entrustment)
    if status:
        query = query.filter(Entrustment.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Entrustment.code.like(like),
                Entrustment.external_no.like(like),
                Entrustment.customer.has(Customer.name.like(like)),
            )
        )
    return [EntrustOut.from_orm(x) for x in query.order_by(Entrustment.id.desc()).limit(limit).all()]


@router.get("/{entrust_id}", response_model=EntrustOut, dependencies=[READER])
def get_entrustment(entrust_id: int, db: Session = Depends(get_db)):
    return EntrustOut.from_orm(_get_or_404(db, entrust_id))


@router.post("", response_model=EntrustOut, status_code=201, dependencies=[WRITER])
def create_entrustment(
    payload: EntrustIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Customer, payload.customer_id) is None:
        raise HTTPException(404, "客户不存在")
    e = Entrustment(
        code=no_entrustment(db),
        customer_id=payload.customer_id,
        requirement=payload.requirement,
        external_no=payload.external_no,
        created_by=user.username,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return EntrustOut.from_orm(e)


@router.patch("/{entrust_id}", response_model=EntrustOut, dependencies=[WRITER])
def update_entrustment(
    entrust_id: int, payload: EntrustUpdate, db: Session = Depends(get_db)
):
    e = _get_or_404(db, entrust_id)
    if e.status not in ("draft", "confirmed"):
        raise HTTPException(409, f"委托单当前状态「{e.status}」不可编辑")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return EntrustOut.from_orm(e)


@router.post("/{entrust_id}/confirm", response_model=EntrustOut, dependencies=[WRITER])
def confirm_entrustment(entrust_id: int, db: Session = Depends(get_db)):
    e = _get_or_404(db, entrust_id)
    _set_status(e, "confirmed", confirmed_at=datetime.utcnow())
    # 里程碑3: 此处按 标准项目 × 样品 自动生成测试任务（钩子）
    db.commit()
    db.refresh(e)
    return EntrustOut.from_orm(e)


@router.post("/{entrust_id}/terminate", response_model=EntrustOut, dependencies=[ADMIN])
def terminate_entrustment(
    entrust_id: int,
    payload: TerminateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = _get_or_404(db, entrust_id)
    _set_status(
        e,
        "terminated",
        terminated_at=datetime.utcnow(),
        terminated_by=user.username,
        terminated_reason=payload.reason,
    )
    db.commit()
    db.refresh(e)
    return EntrustOut.from_orm(e)


@router.post("/from-quote/{quote_id}", response_model=EntrustOut, status_code=201, dependencies=[WRITER])
def create_from_quote(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """已落单报价一键转委托单：继承客户/明细摘要，报价单置「已转委托」。"""
    quote = db.get(Quotation, quote_id)
    if quote is None:
        raise HTTPException(404, "报价单不存在")
    if "converted" not in QUOTE_TRANSITIONS.get(quote.status, ()):
        raise HTTPException(409, f"报价单当前状态「{quote.status}」不可转委托（需已落单）")
    if (
        db.query(Entrustment).filter_by(source_quote_id=quote.id).first() is not None
    ):
        raise HTTPException(409, "该报价单已转过委托")
    e = Entrustment(
        code=no_entrustment(db),
        customer_id=quote.customer_id,
        source_quote_id=quote.id,
        requirement=_quote_items_brief(quote),
        created_by=user.username,
    )
    db.add(e)
    db.flush()
    quote.status = "converted"
    db.commit()
    db.refresh(e)
    return EntrustOut.from_orm(e)
