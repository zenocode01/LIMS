from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_role
from ..models.standard import Equipment, Standard, StandardItem
from ..numbering.service import no_equipment
from ..schemas.standard import EquipmentIn, EquipmentOut, StandardIn, StandardOut

# 权限（设计规格 §5）: 标准库 业务/工程师=查看, 管理=维护/升版
READER = Depends(require_role("business", "engineer", "admin"))
WRITER = Depends(require_role("admin"))

standards_router = APIRouter(prefix="/api/standards", tags=["standards"])
equipment_router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _std_or_404(db: Session, std_id: int) -> Standard:
    s = db.get(Standard, std_id)
    if s is None:
        raise HTTPException(404, "标准不存在")
    return s


def _replace_items(s: Standard, items) -> None:
    s.items = [
        StandardItem(name=i.name, category=i.category, method=i.method, criteria=i.criteria)
        for i in items
    ]


@standards_router.get("", response_model=list[StandardOut], dependencies=[READER])
def list_standards(
    q: str | None = Query(default=None, description="官方号/名称模糊搜索"),
    db: Session = Depends(get_db),
):
    query = db.query(Standard)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Standard.std_no.like(like), Standard.name.like(like)))
    return [StandardOut.from_orm(x) for x in query.order_by(Standard.id).all()]


@standards_router.get("/{std_id}", response_model=StandardOut, dependencies=[READER])
def get_standard(std_id: int, db: Session = Depends(get_db)):
    return StandardOut.from_orm(_std_or_404(db, std_id))


@standards_router.post("", response_model=StandardOut, status_code=201, dependencies=[WRITER])
def create_standard(payload: StandardIn, db: Session = Depends(get_db)):
    if db.query(Standard).filter_by(std_no=payload.std_no).first() is not None:
        raise HTTPException(409, f"标准号 {payload.std_no} 已存在")
    s = Standard(
        std_no=payload.std_no,
        name=payload.name,
        effective_date=payload.effective_date,
        status=payload.status,
    )
    _replace_items(s, payload.items)
    db.add(s)
    db.commit()
    db.refresh(s)
    return StandardOut.from_orm(s)


@standards_router.put("/{std_id}", response_model=StandardOut, dependencies=[WRITER])
def update_standard(std_id: int, payload: StandardIn, db: Session = Depends(get_db)):
    s = _std_or_404(db, std_id)
    s.std_no = payload.std_no
    s.name = payload.name
    s.effective_date = payload.effective_date
    s.status = payload.status
    _replace_items(s, payload.items)
    db.commit()
    db.refresh(s)
    return StandardOut.from_orm(s)


@standards_router.delete("/{std_id}", status_code=204, dependencies=[WRITER])
def delete_standard(std_id: int, db: Session = Depends(get_db)):
    s = _std_or_404(db, std_id)
    db.delete(s)
    db.commit()


@equipment_router.get("", response_model=list[EquipmentOut], dependencies=[READER])
def list_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).order_by(Equipment.id).all()


@equipment_router.post("", response_model=EquipmentOut, status_code=201, dependencies=[WRITER])
def create_equipment(payload: EquipmentIn, db: Session = Depends(get_db)):
    e = Equipment(code=no_equipment(db), name=payload.name, model=payload.model, location=payload.location)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@equipment_router.put("/{eq_id}", response_model=EquipmentOut, dependencies=[WRITER])
def update_equipment(eq_id: int, payload: EquipmentIn, db: Session = Depends(get_db)):
    e = db.get(Equipment, eq_id)
    if e is None:
        raise HTTPException(404, "设备不存在")
    e.name = payload.name
    e.model = payload.model
    e.location = payload.location
    db.commit()
    db.refresh(e)
    return e


@equipment_router.delete("/{eq_id}", status_code=204, dependencies=[WRITER])
def delete_equipment(eq_id: int, db: Session = Depends(get_db)):
    e = db.get(Equipment, eq_id)
    if e is None:
        raise HTTPException(404, "设备不存在")
    db.delete(e)
    db.commit()
    return None
