from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TplFieldIn(BaseModel):
    field_name: str
    field_type: str = "text"
    unit: str | None = None
    required: bool = False
    criteria_expr: str | None = None


class TplIn(BaseModel):
    name: str
    form_level: int = Field(default=4, ge=1, le=4)
    category: str = "EMI"
    controlled: str = "draft"
    version: int = Field(default=1, ge=1)
    fields: list[TplFieldIn] = []


class TplFieldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    field_no: int
    field_name: str
    field_type: str
    unit: str | None
    required: bool
    criteria_expr: str | None


class TplOut(BaseModel):
    id: int
    tpl_no: str
    name: str
    form_level: int
    form_level_label: str
    category: str
    controlled: str
    version: int
    fields: list[TplFieldOut] = []
    field_count: int = 0
    created_at: datetime

    @classmethod
    def from_orm(cls, t) -> "TplOut":
        from ..models.template import FORM_LEVEL_LABELS

        return cls(
            id=t.id,
            tpl_no=t.tpl_no,
            name=t.name,
            form_level=t.form_level,
            form_level_label=FORM_LEVEL_LABELS.get(t.form_level, str(t.form_level)),
            category=t.category,
            controlled=t.controlled,
            version=t.version,
            fields=[TplFieldOut.model_validate(f) for f in t.fields],
            field_count=len(t.fields),
            created_at=t.created_at,
        )
