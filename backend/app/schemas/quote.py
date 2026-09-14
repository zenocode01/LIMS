from datetime import datetime

from pydantic import BaseModel, Field


class QuoteItemIn(BaseModel):
    item_name: str = Field(min_length=1, max_length=128)
    qty: int = Field(default=1, ge=1)
    unit_price: float = Field(default=0, ge=0)


class QuoteIn(BaseModel):
    customer_id: int
    items: list[QuoteItemIn] = Field(min_length=1)
    remark: str | None = None


class QuoteUpdate(BaseModel):
    """仅草稿可编辑（整单替换明细 + 备注）。"""

    items: list[QuoteItemIn] = Field(min_length=1)
    remark: str | None = None


class QuoteItemOut(BaseModel):
    item_name: str
    qty: int
    unit_price: float
    amount: float

    model_config = {"from_attributes": True}


class QuoteOut(BaseModel):
    id: int
    code: str
    status: str
    remark: str | None
    customer_id: int
    customer_name: str
    customer_code: str
    items: list[QuoteItemOut]
    total: float
    created_at: datetime
    updated_at: datetime
    issued_at: datetime | None
    finalized_at: datetime | None


def quote_to_out(q) -> QuoteOut:
    """ORM → Out（含客户名与金额合计，Decimal→float）。"""
    return QuoteOut(
        id=q.id,
        code=q.code,
        status=q.status,
        remark=q.remark,
        customer_id=q.customer_id,
        customer_name=q.customer.name,
        customer_code=q.customer.code,
        items=[
            QuoteItemOut(
                item_name=i.item_name,
                qty=i.qty,
                unit_price=float(i.unit_price),
                amount=round(float(i.unit_price) * i.qty, 2),
            )
            for i in q.items
        ],
        total=round(sum(float(i.unit_price) * i.qty for i in q.items), 2),
        created_at=q.created_at,
        updated_at=q.updated_at,
        issued_at=q.issued_at,
        finalized_at=q.finalized_at,
    )
