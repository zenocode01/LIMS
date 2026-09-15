from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ItemIn(BaseModel):
    name: str
    category: str = "EMI"  # EMI/EMS
    method: str | None = None
    criteria: str | None = None


class StandardIn(BaseModel):
    std_no: str
    name: str
    effective_date: date | None = None
    status: str = "active"
    items: list[ItemIn] = []


class StandardItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    standard_id: int
    name: str
    category: str
    method: str | None
    criteria: str | None


class StandardOut(BaseModel):
    id: int
    std_no: str
    name: str
    effective_date: date | None
    status: str
    items: list[StandardItemOut] = []
    item_count: int = 0

    @classmethod
    def from_orm(cls, s) -> "StandardOut":
        return cls(
            id=s.id,
            std_no=s.std_no,
            name=s.name,
            effective_date=s.effective_date,
            status=s.status,
            items=[StandardItemOut.model_validate(i) for i in s.items],
            item_count=len(s.items),
        )


class EquipmentIn(BaseModel):
    name: str
    model: str | None = None
    location: str | None = None


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    model: str | None
    location: str | None
    created_at: datetime
