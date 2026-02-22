from pydantic import BaseModel, Field
from datetime import datetime

class PlanBase(BaseModel):
    plan_name: str = Field(..., title="Plan Name", max_length=100)
    max_students: int = Field(..., title="Max Students")
    monthly_price: float = Field(..., title="Monthly Price")
    yearly_price: float = Field(..., title="Yearly Price")
    is_active: bool = Field(default=True, title="Is Active")

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    plan_name: str | None = Field(None, title="Plan Name", max_length=100)
    max_students: int | None = Field(None, title="Max Students")
    monthly_price: float | None = Field(None, title="Monthly Price")
    yearly_price: float | None = Field(None, title="Yearly Price")
    is_active: bool | None = Field(None, title="Is Active")

class PlanResponse(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
