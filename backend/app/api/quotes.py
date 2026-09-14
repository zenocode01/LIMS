from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_role
from ..models.customer import Customer
from ..models.quote import QUOTE_TRANSITIONS, Quotation, QuotationItem
from ..numbering.service import no_quote
from ..schemas.quote import QuoteIn, QuoteOut, QuoteUpdate, quote_to_out

READER = Depends(require_role("business", "admin"))  # 读: 业务+管理
WRITER = Depends(require_role("business"))  # 写/状态迁移: 仅业务

router = APIRouter(prefix="/api/quotations", tags=["quotations"])


def _get_or_404(db: Session, quote_id: int) -> Quotation:
    q = db.get(Quotation, quote_id)
    if q is None:
        raise HTTPException(404, "报价单不存在")
    return q


def _set_status(q: Quotation, to: str, **fields) -> None:
    """状态机守卫：非法迁移 409。"""
    if to not in QUOTE_TRANSITIONS.get(q.status, ()):
        raise HTTPException(409, f"报价单当前状态「{q.status}」不允许迁移到「{to}」")
    q.status = to
    for k, v in fields.items():
        setattr(q, k, v)


def _replace_items(q: Quotation, items) -> None:
    q.items = [
        QuotationItem(item_name=i.item_name, qty=i.qty, unit_price=i.unit_price) for i in items
    ]


@router.get("", response_model=list[QuoteOut], dependencies=[READER])
def list_quotes(
    q: str | None = Query(default=None, description="编号/客户名称模糊搜索"),
    status: str | None = Query(default=None, description="状态过滤"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Quotation)
    if status:
        query = query.filter(Quotation.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(Quotation.code.like(like), Quotation.customer.has(Customer.name.like(like)))
        )
    return [quote_to_out(x) for x in query.order_by(Quotation.id.desc()).limit(limit).all()]


@router.get("/{quote_id}", response_model=QuoteOut, dependencies=[READER])
def get_quote(quote_id: int, db: Session = Depends(get_db)):
    return quote_to_out(_get_or_404(db, quote_id))


@router.post("", response_model=QuoteOut, status_code=201, dependencies=[WRITER])
def create_quote(body: QuoteIn, db: Session = Depends(get_db)):
    if db.get(Customer, body.customer_id) is None:
        raise HTTPException(404, "客户不存在")
    quote = Quotation(code=no_quote(db), customer_id=body.customer_id, remark=body.remark)
    _replace_items(quote, body.items)
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote_to_out(quote)


@router.patch("/{quote_id}", response_model=QuoteOut, dependencies=[WRITER])
def update_quote(quote_id: int, body: QuoteUpdate, db: Session = Depends(get_db)):
    quote = _get_or_404(db, quote_id)
    if quote.status != "draft":
        raise HTTPException(409, "仅草稿状态的报价单可编辑")
    _replace_items(quote, body.items)
    quote.remark = body.remark
    db.commit()
    db.refresh(quote)
    return quote_to_out(quote)


@router.post("/{quote_id}/issue", response_model=QuoteOut, dependencies=[WRITER])
def issue_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = _get_or_404(db, quote_id)
    _set_status(quote, "issued", issued_at=datetime.utcnow())
    db.commit()
    db.refresh(quote)
    return quote_to_out(quote)


@router.post("/{quote_id}/finalize", response_model=QuoteOut, dependencies=[WRITER])
def finalize_quote(quote_id: int, db: Session = Depends(get_db)):
    """客户接受报价（落单）。"""
    quote = _get_or_404(db, quote_id)
    _set_status(quote, "finalized", finalized_at=datetime.utcnow())
    db.commit()
    db.refresh(quote)
    return quote_to_out(quote)


@router.post("/{quote_id}/cancel", response_model=QuoteOut, dependencies=[WRITER])
def cancel_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = _get_or_404(db, quote_id)
    _set_status(quote, "cancelled")
    db.commit()
    db.refresh(quote)
    return quote_to_out(quote)
