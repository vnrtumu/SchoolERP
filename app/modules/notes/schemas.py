from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    color: str = "primary"


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    color: str | None = None
    deleted: bool | None = None


class NoteResponse(NoteBase):
    id: int
    user_id: int
    datef: datetime
    deleted: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
