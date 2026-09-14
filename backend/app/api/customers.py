from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user, require_role
from ..models.customer import Customer
from ..models.user import User
from ..numbering.service import no_customer
from ..schemas.customer import CustomerIn, CustomerOut, CustomerUpdate

READER = Depends(require_role("business", "admin"))  # 读: 业务+管理
WRITER = Depends(require_role("business"))  # 写: 仅业务

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _get_or_404(db: Session, customer_id: int) -> Customer:
    c = db.get(Customer, customer_id)
    if c is None:
        raise HTTPException(404, "客户不存在")
    return c


@router.get("", response_model=list[CustomerOut], dependencies=[READER])
def list_customers(
    q: str | None = Query(default=None, description="名称/编号/行业模糊搜索"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.name.like(like),
                Customer.code.like(like),
                Customer.industry.like(like),
            )
        )
    return query.order_by(Customer.id.desc()).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerOut, dependencies=[READER])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, customer_id)


@router.post("", response_model=CustomerOut, status_code=201, dependencies=[WRITER])
def create_customer(body: CustomerIn, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.name == body.name).first():
        raise HTTPException(409, "客户名称已存在")
    c = Customer(code=no_customer(db), **body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/{customer_id}", response_model=CustomerOut, dependencies=[WRITER])
def update_customer(
    customer_id: int, body: CustomerUpdate, db: Session = Depends(get_db)
):
    c = _get_or_404(db, customer_id)
    # exclude_unset: 前端传 null = 清空字段（exclude_none 会把清空吞掉）
    data = body.model_dump(exclude_unset=True)
    if "name" in data:
        dup = (
            db.query(Customer)
            .filter(Customer.name == data["name"], Customer.id != c.id)
            .first()
        )
        if dup:
            raise HTTPException(409, "客户名称已存在")
    for k, v in data.items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{customer_id}", status_code=204, dependencies=[WRITER])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    c = _get_or_404(db, customer_id)
    db.delete(c)
    db.commit()
