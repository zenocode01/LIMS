from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 样品状态机（设计规格 §3）: 已登记 → 在测 → 已返 → 已报废
# 每次变更写一条 SampleEvent 流转留痕（操作人/时间/备注）。
SAMPLE_STATUSES = ("registered", "in_test", "returned", "disposed")
SAMPLE_TRANSITIONS = {
    "registered": ("in_test",),
    "in_test": ("returned",),
    "returned": ("disposed",),
    "disposed": (),
}
SAMPLE_STATUS_LABELS = {
    "registered": "已登记",
    "in_test": "在测",
    "returned": "已返",
    "disposed": "已报废",
}


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 样品编号: S-{业务线}-YYYYMMDD-流水（业务线=EMC 伞类, 按日归零, 设计规格 §7）
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    biz_line: Mapped[str] = mapped_column(String(16), default="EMC")
    entrustment_id: Mapped[int] = mapped_column(ForeignKey("entrustments.id"), index=True)
    name_model: Mapped[str] = mapped_column(String(128))
    appearance: Mapped[str | None] = mapped_column(String(256), nullable=True)
    external_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="registered", index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    entrustment = relationship("Entrustment", lazy="joined")
    events = relationship(
        "SampleEvent",
        cascade="all, delete-orphan",
        order_by="SampleEvent.created_at.desc(), SampleEvent.id.desc()",
    )


class SampleEvent(Base):
    """样品流转留痕: 每次状态变更一条，不可改（只增不删）。"""

    __tablename__ = "sample_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str] = mapped_column(String(16))
    operator: Mapped[str | None] = mapped_column(String(64), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
