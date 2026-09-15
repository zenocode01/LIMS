from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 报价状态机（设计规格 §6 主流程）:
#   草稿 ──发出──> 已发出 ──客户接受(落单)──> 已落单 ──转委托──> 已转委托(终态, T-015 接通)
#   草稿/已发出 ──取消──> 已取消(终态)
QUOTE_STATUSES = ("draft", "issued", "finalized", "converted", "cancelled")
QUOTE_TRANSITIONS = {
    "draft": ("issued", "cancelled"),
    "issued": ("finalized", "cancelled"),
    "finalized": ("converted",),
    "converted": (),
    "cancelled": (),
}
QUOTE_STATUS_LABELS = {
    "draft": "草稿",
    "issued": "已发出",
    "finalized": "已落单",
    "converted": "已转委托",
    "cancelled": "已取消",
}


class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="draft", index=True)
    remark: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    issued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    customer = relationship("Customer", lazy="joined")
    items = relationship(
        "QuotationItem",
        cascade="all, delete-orphan",
        order_by="QuotationItem.id",
    )


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id: Mapped[int] = mapped_column(ForeignKey("quotations.id"), index=True)
    # 标准项目引用（T-018 标准库上线后接通）; 为空时以 item_name 文本承载
    standard_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("standard_items.id"), nullable=True, index=True
    )
    item_name: Mapped[str] = mapped_column(String(128))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    standard_item = relationship("StandardItem", lazy="joined")
