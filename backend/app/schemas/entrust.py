from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntrustIn(BaseModel):
    customer_id: int
    requirement: str | None = None
    external_no: str | None = None


class EntrustUpdate(BaseModel):
    requirement: str | None = None
    external_no: str | None = None


class TerminateIn(BaseModel):
    reason: str | None = None


class EntrustOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    customer_id: int
    customer_name: str
    source_quote_id: int | None = None
    source_quote_code: str | None = None
    requirement: str | None
    external_no: str | None
    status: str
    status_label: str
    created_by: str | None
    created_at: datetime | None
    confirmed_at: datetime | None
    terminated_at: datetime | None
    terminated_by: str | None
    terminated_reason: str | None

    @classmethod
    def from_orm(cls, e) -> "EntrustOut":
        from ..models.entrust import ENTRUST_STATUS_LABELS

        return cls(
            id=e.id,
            code=e.code,
            customer_id=e.customer_id,
            customer_name=e.customer.name if e.customer else "",
            source_quote_id=e.source_quote_id,
            source_quote_code=e.source_quote.code if e.source_quote else None,
            requirement=e.requirement,
            external_no=e.external_no,
            status=e.status,
            status_label=ENTRUST_STATUS_LABELS.get(e.status, e.status),
            created_by=e.created_by,
            created_at=e.created_at,
            confirmed_at=e.confirmed_at,
            terminated_at=e.terminated_at,
            terminated_by=e.terminated_by,
            terminated_reason=e.terminated_reason,
        )
