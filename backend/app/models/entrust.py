from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 委托单状态机（设计规格 §3）:
#   草稿 ──业务确认──> 已确认 ──首个任务开测(M3)──> 测试中 ──全部报告签发(M4)──> 已出报告
#        ──样品返还后业务手动关闭──> 已完成
#   任意非终态 ──管理终止──> 已终止(终态)
# M2 范围: draft→confirmed 与 *→terminated 可走; testing/report_issued/completed
# 的触发依赖任务/样品模块（M3/M4），端点已留守卫, 届时接通。
ENTRUST_STATUSES = ("draft", "confirmed", "testing", "report_issued", "completed", "terminated")
ENTRUST_TRANSITIONS = {
    "draft": ("confirmed", "terminated"),
    "confirmed": ("testing", "terminated"),
    "testing": ("report_issued", "terminated"),
    "report_issued": ("completed", "terminated"),
    "completed": (),
    "terminated": (),
}
ENTRUST_STATUS_LABELS = {
    "draft": "草稿",
    "confirmed": "已确认",
    "testing": "测试中",
    "report_issued": "已出报告",
    "completed": "已完成",
    "terminated": "已终止",
}


class Entrustment(Base):
    __tablename__ = "entrustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 委托单编号: C-YYYYMMDD-流水, 全局/日, 主线（设计规格 §7）
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    # 来源报价单（一键转入时回填; 手工新建为空）
    source_quote_id: Mapped[int | None] = mapped_column(
        ForeignKey("quotations.id"), nullable=True, index=True
    )
    # 委托要求: 转入时预填报价明细摘要, 业务可改
    requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 客户侧委托编号（对账用）
    external_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="draft", index=True)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    terminated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    terminated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    terminated_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)

    customer = relationship("Customer", lazy="joined")
    source_quote = relationship("Quotation", lazy="joined")
    tasks = relationship("Task")
