from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SampleIn(BaseModel):
    entrustment_id: int
    name_model: str
    appearance: str | None = None
    external_no: str | None = None


class TransitionIn(BaseModel):
    to: str
    note: str | None = None


class SampleEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: str | None
    to_status: str
    to_status_label: str
    operator: str | None
    note: str | None
    created_at: datetime

    @classmethod
    def from_orm(cls, ev) -> "SampleEventOut":
        from ..models.sample import SAMPLE_STATUS_LABELS

        return cls(
            from_status=ev.from_status,
            to_status=ev.to_status,
            to_status_label=SAMPLE_STATUS_LABELS.get(ev.to_status, ev.to_status),
            operator=ev.operator,
            note=ev.note,
            created_at=ev.created_at,
        )


class SampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    biz_line: str
    entrustment_id: int
    entrustment_code: str
    name_model: str
    appearance: str | None
    external_no: str | None
    status: str
    status_label: str
    created_by: str | None
    created_at: datetime
    events: list[SampleEventOut] = []

    @classmethod
    def from_orm(cls, s) -> "SampleOut":
        from ..models.sample import SAMPLE_STATUS_LABELS

        return cls(
            id=s.id,
            code=s.code,
            biz_line=s.biz_line,
            entrustment_id=s.entrustment_id,
            entrustment_code=s.entrustment.code if s.entrustment else "",
            name_model=s.name_model,
            appearance=s.appearance,
            external_no=s.external_no,
            status=s.status,
            status_label=SAMPLE_STATUS_LABELS.get(s.status, s.status),
            created_by=s.created_by,
            created_at=s.created_at,
            events=[SampleEventOut.from_orm(ev) for ev in s.events],
        )
