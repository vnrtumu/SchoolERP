from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.tenancy.database import get_master_db
from app.core.dependencies import get_current_super_admin
from app.tenancy.models import SuperAdmin, Note
from .schemas import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter()

@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    current_admin: SuperAdmin = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Retrieve all non-deleted personal sticky notes for the current super admin.
    """
    user_id = current_admin.get("sub")
    query = select(Note).where(Note.user_id == user_id, Note.deleted == False).order_by(Note.created_at.desc())
    result = await db.execute(query)
    notes = result.scalars().all()
    return notes


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    current_admin: SuperAdmin = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Create a new personal sticky note for the current super admin.
    """
    user_id = current_admin.get("sub")
    new_note = Note(
        user_id=user_id,
        title=note_in.title,
        color=note_in.color
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_in: NoteUpdate,
    current_admin: SuperAdmin = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Update an existing sticky note (title, color, or deleted status).
    """
    user_id = current_admin.get("sub")
    query = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    result = await db.execute(query)
    note = result.scalars().first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
        
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_admin: SuperAdmin = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_master_db)
):
    """
    Soft-delete a sticky note.
    """
    user_id = current_admin.get("sub")
    query = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    result = await db.execute(query)
    note = result.scalars().first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    note.deleted = True
    await db.commit()
    
    return None
