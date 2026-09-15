from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 标准库（设计规格 §8）:
# - standards: 不自定义编号, 用官方标准号（GB 9254-2028 等）
# - standard_items: 测试项目（标准/名称/类别 EMI|EMS/方法/判据）
#   类别是属性字段不入编号; 关联记录模板在记录模板库（T-019）落地
ITEM_CATEGORIES = ("EMI", "EMS")


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    std_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)  # active/obsolete
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    items = relationship(
        "StandardItem",
        cascade="all, delete-orphan",
        order_by="StandardItem.id",
    )


class StandardItem(Base):
    __tablename__ = "standard_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    standard_id: Mapped[int] = mapped_column(
        ForeignKey("standards.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(8), default="EMI", index=True)  # EMI/EMS
    method: Mapped[str | None] = mapped_column(String(256), nullable=True)
    criteria: Mapped[str | None] = mapped_column(String(512), nullable=True)

    standard = relationship("Standard", lazy="joined")


class Equipment(Base):
    """设备简表（设计规格 §8: 编号/名称/型号/位置, P2 档案深化）。"""

    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)  # EQ-NNN 静态
    name: Mapped[str] = mapped_column(String(64))
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    location: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
