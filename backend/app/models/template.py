from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# 记录模板库（设计规格 §8）:
# - record_templates: 模板编号(3位, 静态流水)/名称/表单层级(1-4)/类别/受控状态/版本
# - template_fields: 字段定义（模板=字段定义, 一次投入长期复用）
# 表单层级: 1=手册 2=程序文件 3=作业指导书 4=纯记录表单（入记录编号第 2 段）
FORM_LEVELS = (1, 2, 3, 4)
FORM_LEVEL_LABELS = {1: "手册", 2: "程序文件", 3: "作业指导书", 4: "纯记录表单"}
FIELD_TYPES = ("text", "number", "date", "select")
CONTROLLED_STATES = ("draft", "controlled", "obsolete")


class RecordTemplate(Base):
    __tablename__ = "record_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tpl_no: Mapped[str] = mapped_column(String(8), unique=True, index=True)  # 3 位: 001
    name: Mapped[str] = mapped_column(String(128))
    form_level: Mapped[int] = mapped_column(Integer, default=4)  # 1-4
    category: Mapped[str] = mapped_column(String(8), default="EMI", index=True)  # EMI/EMS/common
    controlled: Mapped[str] = mapped_column(String(16), default="draft", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    fields = relationship(
        "TemplateField",
        cascade="all, delete-orphan",
        order_by="TemplateField.field_no, TemplateField.id",
    )


class TemplateField(Base):
    __tablename__ = "template_fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("record_templates.id"), index=True
    )
    field_no: Mapped[int] = mapped_column(Integer, default=0)
    field_name: Mapped[str] = mapped_column(String(64))
    field_type: Mapped[str] = mapped_column(String(16), default="text")  # text/number/date/select
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    criteria_expr: Mapped[str | None] = mapped_column(String(256), nullable=True)

    template = relationship("RecordTemplate", lazy="joined")
