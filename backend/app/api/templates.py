from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_role
from ..models.template import FIELD_TYPES, RecordTemplate, TemplateField
from ..numbering.service import no_record_template
from ..schemas.template import TplFieldIn, TplIn, TplOut

# 权限（设计规格 §5）: 标准库/模板 业务/工程师=查看, 管理=维护/升版
READER = Depends(require_role("business", "engineer", "admin"))
WRITER = Depends(require_role("admin"))

router = APIRouter(prefix="/api/record-templates", tags=["record-templates"])


def _get_or_404(db: Session, tpl_id: int) -> RecordTemplate:
    t = db.get(RecordTemplate, tpl_id)
    if t is None:
        raise HTTPException(404, "记录模板不存在")
    return t


def _replace_fields(t: RecordTemplate, fields: list[TplFieldIn]) -> None:
    t.fields = [
        TemplateField(
            field_no=i,
            field_name=f.field_name,
            field_type=f.field_type if f.field_type in FIELD_TYPES else "text",
            unit=f.unit,
            required=f.required,
            criteria_expr=f.criteria_expr,
        )
        for i, f in enumerate(fields, start=1)
    ]


@router.get("", response_model=list[TplOut], dependencies=[READER])
def list_templates(
    q: str | None = Query(default=None, description="编号/名称模糊搜索"),
    db: Session = Depends(get_db),
):
    query = db.query(RecordTemplate)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(RecordTemplate.tpl_no.like(like), RecordTemplate.name.like(like)))
    return [TplOut.from_orm(x) for x in query.order_by(RecordTemplate.id).all()]


@router.get("/{tpl_id}", response_model=TplOut, dependencies=[READER])
def get_template(tpl_id: int, db: Session = Depends(get_db)):
    return TplOut.from_orm(_get_or_404(db, tpl_id))


@router.post("", response_model=TplOut, status_code=201, dependencies=[WRITER])
def create_template(payload: TplIn, db: Session = Depends(get_db)):
    t = RecordTemplate(
        tpl_no=no_record_template(db),
        name=payload.name,
        form_level=payload.form_level,
        category=payload.category,
        controlled=payload.controlled,
        version=payload.version,
    )
    _replace_fields(t, payload.fields)
    db.add(t)
    db.commit()
    db.refresh(t)
    return TplOut.from_orm(t)


@router.put("/{tpl_id}", response_model=TplOut, dependencies=[WRITER])
def update_template(tpl_id: int, payload: TplIn, db: Session = Depends(get_db)):
    t = _get_or_404(db, tpl_id)
    t.name = payload.name
    t.form_level = payload.form_level
    t.category = payload.category
    t.controlled = payload.controlled
    t.version = payload.version
    _replace_fields(t, payload.fields)
    db.commit()
    db.refresh(t)
    return TplOut.from_orm(t)


@router.delete("/{tpl_id}", status_code=204, dependencies=[WRITER])
def delete_template(tpl_id: int, db: Session = Depends(get_db)):
    t = _get_or_404(db, tpl_id)
    db.delete(t)
    db.commit()
    return None
