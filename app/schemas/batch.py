from pydantic import BaseModel, Field


class BatchCreate(BaseModel): filenames: list[str] = Field(default_factory=list, max_length=20)
class ScanItemCreate(BaseModel):
    original_filename: str
    original_size: int | None = None
