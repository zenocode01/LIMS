from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 测试任务（设计规格 §3/§8）: 任务即工单，= 标准项目 × 样品
# 状态机: 未排程 → 已排程 → 测试中 → 完成；打回重测: 完成 → 测试中（管理触发、留原因）
# 类别 EMI/EMS 继承自标准项目（属性字段, 不入编号）。
TASK_STATUSES = ("unscheduled", "scheduled", "testing", "completed")
TASK_TRANSITIONS = {
    "unscheduled": ("scheduled", "testing"),
    "scheduled": ("testing",),
    "testing": ("completed",),
    "completed": ("testing",),  # 打回重测（仅管理, API 层守卫）
}
TASK_STATUS_LABELS = {
    "unscheduled": "未排程",
    "scheduled": "已排程",
    "testing": "测试中",
    "completed": "完成",
}


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)  # T-YYYYMMDD-NNN
    entrustment_id: Mapped[int] = mapped_column(ForeignKey("entrustments.id"), index=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey("samples.id"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("standard_items.id"), index=True)
    category: Mapped[str] = mapped_column(String(8), default="EMI", index=True)  # 继承自项目
    status: Mapped[str] = mapped_column(String(16), default="unscheduled", index=True)
    retest_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    entrustment = relationship("Entrustment", lazy="joined", overlaps="tasks")
    sample = relationship("Sample", lazy="joined")
    item = relationship("StandardItem", lazy="joined")
