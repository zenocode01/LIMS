from datetime import datetime

from pydantic import BaseModel


class CustomerIn(BaseModel):
    name: str
    industry: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    remark: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    remark: str | None = None


class CustomerOut(BaseModel):
    id: int
    code: str
    name: str
    industry: str | None
    contact_name: str | None
    contact_phone: str | None
    remark: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
