from pydantic import BaseModel, Field


class ExportCreate(BaseModel):
    mode: str = Field('unexported', pattern='^(unexported|all_approved|selected|batch)$')
    scan_item_ids: list[str] = Field(default_factory=list)
    batch_id: str | None = None
