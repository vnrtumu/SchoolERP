from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.tenancy.database import get_master_db
from app.core.dependencies import get_current_super_admin
from app.tenancy.models import SuperAdmin, Ticket
from .schemas import TicketCreate, TicketUpdate, TicketResponse

router = APIRouter()

@router.get("/", response_model=List[TicketResponse])
async def get_tickets(
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Retrieve all non-deleted tickets for the current super admin.
    """
    user_id = current_admin.get("sub")
    query = select(Ticket).where(Ticket.user_id == user_id, Ticket.deleted == False).order_by(Ticket.Date.desc())
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Create a new ticket.
    """
    user_id = current_admin.get("sub")
    new_ticket = Ticket(
        user_id=user_id,
        **ticket_in.model_dump()
    )
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return new_ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Update an existing ticket.
    """
    user_id = current_admin.get("sub")
    query = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    update_data = ticket_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
        
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    current_admin=Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Soft-delete a ticket.
    """
    user_id = current_admin.get("sub")
    query = select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user_id)
    result = await db.execute(query)
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    ticket.deleted = True
    await db.commit()
    
    return None
