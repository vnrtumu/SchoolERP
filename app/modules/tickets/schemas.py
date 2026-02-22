from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class TicketBase(BaseModel):
    ticketTitle: str
    ticketDescription: str
    Status: str = "Open"
    Label: str = "success"
    thumb: Optional[str] = None
    AgentName: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    ticketTitle: Optional[str] = None
    ticketDescription: Optional[str] = None
    Status: Optional[str] = None
    Label: Optional[str] = None
    thumb: Optional[str] = None
    AgentName: Optional[str] = None
    deleted: Optional[bool] = None


class TicketResponse(TicketBase):
    Id: int = Field(validation_alias="id")
    Date: datetime
    deleted: bool
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
