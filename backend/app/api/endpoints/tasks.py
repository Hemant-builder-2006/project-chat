"""Task endpoints for TODO list functionality."""
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.channel import Channel, ChannelType
from app.models.task import Task
from app.models.membership import Membership
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead

router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def check_todo_channel_access(channel_id: str, user_id: str, db: AsyncSession) -> Channel:
    """Verify user has access to TODO channel."""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    if channel.type != ChannelType.TODO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Channel is not a TODO channel"
        )
    
    # Check group membership
    result = await db.execute(
        select(Membership).where(
            Membership.group_id == channel.group_id,
            Membership.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    return channel


@router.get("/channels/{channel_id}", response_model=List[TaskRead])
async def get_channel_tasks(
    channel_id: str,
    completed: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all tasks in a TODO channel."""
    
    # Verify access
    await check_todo_channel_access(channel_id, current_user.id, db)
    
    # Build query
    query = select(Task).where(Task.channel_id == channel_id)
    
    # Filter by completion status
    if completed is not None:
        query = query.where(Task.is_completed == completed)
    
    # Order by position
    query = query.order_by(Task.position).options(
        selectinload(Task.creator),
        selectinload(Task.assignee)
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks


@router.post("/channels/{channel_id}", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    channel_id: str,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new task in a TODO channel."""
    
    # Verify access
    await check_todo_channel_access(channel_id, current_user.id, db)
    
    # Verify assignee is member of group (if provided)
    if task_data.assigned_to_id:
        result = await db.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        channel = result.scalar_one()
        
        result = await db.execute(
            select(Membership).where(
                Membership.group_id == channel.group_id,
                Membership.user_id == task_data.assigned_to_id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of this group"
            )
    
    # Get max position
    result = await db.execute(
        select(Task.position)
        .where(Task.channel_id == channel_id)
        .order_by(Task.position.desc())
        .limit(1)
    )
    max_position = result.scalar_one_or_none()
    next_position = (max_position or 0) + 1
    
    # Create task
    task = Task(
        content=task_data.content,
        channel_id=channel_id,
        created_by_id=current_user.id,
        assigned_to_id=task_data.assigned_to_id,
        position=next_position
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task, ["creator", "assignee"])
    
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get a specific task."""
    
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(
            selectinload(Task.channel),
            selectinload(Task.creator),
            selectinload(Task.assignee)
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify access
    await check_todo_channel_access(task.channel_id, current_user.id, db)
    
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update a task."""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify access
    await check_todo_channel_access(task.channel_id, current_user.id, db)
    
    # Update fields
    if task_data.content is not None:
        task.content = task_data.content
    
    if task_data.is_completed is not None:
        task.is_completed = task_data.is_completed
    
    if task_data.assigned_to_id is not None:
        # Verify assignee
        result = await db.execute(
            select(Channel).where(Channel.id == task.channel_id)
        )
        channel = result.scalar_one()
        
        result = await db.execute(
            select(Membership).where(
                Membership.group_id == channel.group_id,
                Membership.user_id == task_data.assigned_to_id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of this group"
            )
        
        task.assigned_to_id = task_data.assigned_to_id
    
    if task_data.position is not None:
        task.position = task_data.position
    
    await db.commit()
    await db.refresh(task, ["creator", "assignee"])
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete a task."""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify access
    await check_todo_channel_access(task.channel_id, current_user.id, db)
    
    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Toggle task completion status."""
    
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify access
    await check_todo_channel_access(task.channel_id, current_user.id, db)
    
    # Toggle completion
    task.is_completed = not task.is_completed
    
    await db.commit()
    await db.refresh(task, ["creator", "assignee"])
    
    return task


@router.put("/channels/{channel_id}/reorder", response_model=List[TaskRead])
async def reorder_tasks(
    channel_id: str,
    task_ids: List[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Reorder tasks in a TODO channel."""
    
    # Verify access
    await check_todo_channel_access(channel_id, current_user.id, db)
    
    # Update positions
    for position, task_id in enumerate(task_ids):
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.channel_id == channel_id
                )
            )
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.position = position
    
    await db.commit()
    
    # Return updated list
    result = await db.execute(
        select(Task)
        .where(Task.channel_id == channel_id)
        .order_by(Task.position)
        .options(selectinload(Task.creator), selectinload(Task.assignee))
    )
    tasks = result.scalars().all()
    
    return tasks
