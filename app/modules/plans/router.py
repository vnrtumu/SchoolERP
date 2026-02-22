from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.tenancy.database import get_master_db
from app.tenancy.models import SubscriptionPlan
from app.core.dependencies import get_current_super_admin
from .schemas import PlanCreate, PlanUpdate, PlanResponse

router = APIRouter()

@router.get("/", response_model=List[PlanResponse])
async def get_all_plans(
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Retrieve all configuration subscription plans.
    """
    result = await db.execute(select(SubscriptionPlan).order_by(SubscriptionPlan.monthly_price))
    plans = result.scalars().all()
    return plans


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Create a new subscription plan.
    """
    # Check for existing plan with same name
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.plan_name == plan_data.plan_name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan '{plan_data.plan_name}' already exists"
        )
    
    new_plan = SubscriptionPlan(**plan_data.model_dump())
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    return new_plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Delete a subscription plan.
    """
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        
    await db.delete(plan)
    await db.commit()
    
    return None
