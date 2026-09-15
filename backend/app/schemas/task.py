from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    entrustment_id: int
    entrustment_code: str
    sample_id: int
    sample_code: str
    sample_name: str
    item_id: int
    item_name: str
    category: str
    status: str
    status_label: str
    retest_reason: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    @classmethod
    def from_orm(cls, t) -> "TaskOut":
        from ..models.task import TASK_STATUS_LABELS

        return cls(
            id=t.id,
            code=t.code,
            entrustment_id=t.entrustment_id,
            entrustment_code=t.entrustment.code if t.entrustment else "",
            sample_id=t.sample_id,
            sample_code=t.sample.code if t.sample else "",
            sample_name=t.sample.name_model if t.sample else "",
            item_id=t.item_id,
            item_name=t.item.name if t.item else "",
            category=t.category,
            status=t.status,
            status_label=TASK_STATUS_LABELS.get(t.status, t.status),
            retest_reason=t.retest_reason,
            created_at=t.created_at,
            started_at=t.started_at,
            completed_at=t.completed_at,
        )
