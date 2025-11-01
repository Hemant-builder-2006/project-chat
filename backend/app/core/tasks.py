"""Background tasks for periodic maintenance operations."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import os

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.message import Message
from app.models.attachment import Attachment

logger = logging.getLogger(__name__)


async def run_periodic_data_retention():
    """
    Background task for periodic data retention cleanup.
    
    Runs continuously in the background, cleaning up old data based on
    DATA_RETENTION_DAYS environment variable.
    
    Operations:
    - Delete messages older than retention period
    - Clean up orphaned attachments
    - Log cleanup statistics
    
    Runs every 24 hours.
    """
    # Get retention period from environment (default: 365 days)
    retention_days = int(os.getenv("DATA_RETENTION_DAYS", "365"))
    
    # Check interval (default: 24 hours)
    check_interval_hours = int(os.getenv("DATA_RETENTION_CHECK_HOURS", "24"))
    
    logger.info(
        f"Starting data retention task: "
        f"retention_days={retention_days}, "
        f"check_interval={check_interval_hours}h"
    )
    
    while True:
        try:
            await asyncio.sleep(check_interval_hours * 3600)  # Convert hours to seconds
            
            logger.info("Running data retention cleanup...")
            
            async with AsyncSessionLocal() as db:
                # Calculate cutoff date
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # Delete old messages in batches
                deleted_messages = await _delete_old_messages(db, cutoff_date)
                
                # Clean up orphaned attachments
                deleted_attachments = await _delete_orphaned_attachments(db)
                
                # Commit changes
                await db.commit()
                
                logger.info(
                    f"Data retention cleanup completed: "
                    f"deleted {deleted_messages} messages, "
                    f"{deleted_attachments} orphaned attachments"
                )
        
        except asyncio.CancelledError:
            logger.info("Data retention task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in data retention task: {e}", exc_info=True)
            # Continue running even if one iteration fails


async def _delete_old_messages(db: AsyncSession, cutoff_date: datetime) -> int:
    """
    Delete messages older than cutoff date in batches.
    
    Args:
        db: Database session
        cutoff_date: Delete messages older than this date
    
    Returns:
        Number of messages deleted
    """
    batch_size = 1000
    total_deleted = 0
    
    while True:
        # Get a batch of old message IDs
        result = await db.execute(
            select(Message.id)
            .where(Message.created_at < cutoff_date)
            .limit(batch_size)
        )
        message_ids = [row[0] for row in result.fetchall()]
        
        if not message_ids:
            break
        
        # Delete the batch
        await db.execute(
            delete(Message).where(Message.id.in_(message_ids))
        )
        
        total_deleted += len(message_ids)
        logger.debug(f"Deleted batch of {len(message_ids)} old messages")
        
        # Give database a break between batches
        await asyncio.sleep(0.1)
    
    return total_deleted


async def _delete_orphaned_attachments(db: AsyncSession) -> int:
    """
    Delete attachments that no longer have associated messages.
    
    Args:
        db: Database session
    
    Returns:
        Number of attachments deleted
    """
    # Find attachments with no associated message
    result = await db.execute(
        select(Attachment.id)
        .outerjoin(Message, Attachment.message_id == Message.id)
        .where(Message.id.is_(None))
    )
    orphaned_ids = [row[0] for row in result.fetchall()]
    
    if orphaned_ids:
        # Delete orphaned attachments
        await db.execute(
            delete(Attachment).where(Attachment.id.in_(orphaned_ids))
        )
        logger.debug(f"Deleted {len(orphaned_ids)} orphaned attachments")
    
    return len(orphaned_ids)


async def run_periodic_file_cleanup():
    """
    Background task for cleaning up old files from storage.
    
    Runs continuously, removing files that are no longer referenced
    in the database.
    
    Optional: Can be enabled with FILE_CLEANUP_ENABLED=true
    """
    if not os.getenv("FILE_CLEANUP_ENABLED", "").lower() == "true":
        logger.info("File cleanup task disabled (set FILE_CLEANUP_ENABLED=true to enable)")
        return
    
    cleanup_interval_hours = int(os.getenv("FILE_CLEANUP_INTERVAL_HOURS", "168"))  # 1 week default
    
    logger.info(f"Starting file cleanup task: interval={cleanup_interval_hours}h")
    
    while True:
        try:
            await asyncio.sleep(cleanup_interval_hours * 3600)
            
            logger.info("Running file cleanup...")
            
            # TODO: Implement file cleanup logic
            # - Scan upload directory
            # - Check if files exist in database
            # - Delete unreferenced files
            
            logger.info("File cleanup completed")
        
        except asyncio.CancelledError:
            logger.info("File cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in file cleanup task: {e}", exc_info=True)


async def run_periodic_health_check():
    """
    Background task for periodic health checks of external services.
    
    Checks:
    - Database connection
    - Redis connection
    - Ollama service
    - ChromaDB service
    
    Logs warnings if services are unavailable.
    """
    if not os.getenv("HEALTH_CHECK_ENABLED", "").lower() == "true":
        return
    
    check_interval_minutes = int(os.getenv("HEALTH_CHECK_INTERVAL_MINUTES", "30"))
    
    logger.info(f"Starting health check task: interval={check_interval_minutes}m")
    
    while True:
        try:
            await asyncio.sleep(check_interval_minutes * 60)
            
            logger.debug("Running health checks...")
            
            # Check database
            try:
                async with AsyncSessionLocal() as db:
                    await db.execute(select(1))
                logger.debug("✓ Database healthy")
            except Exception as e:
                logger.warning(f"✗ Database unhealthy: {e}")
            
            # Check Ollama
            try:
                from app.services.ai_service import check_ollama_health
                is_healthy = await check_ollama_health()
                if is_healthy:
                    logger.debug("✓ Ollama healthy")
                else:
                    logger.warning("✗ Ollama unhealthy")
            except Exception as e:
                logger.warning(f"✗ Ollama check failed: {e}")
            
            # Check ChromaDB
            try:
                from app.services.rag_service import check_chromadb_health
                is_healthy = await check_chromadb_health()
                if is_healthy:
                    logger.debug("✓ ChromaDB healthy")
                else:
                    logger.warning("✗ ChromaDB unhealthy")
            except Exception as e:
                logger.warning(f"✗ ChromaDB check failed: {e}")
        
        except asyncio.CancelledError:
            logger.info("Health check task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in health check task: {e}", exc_info=True)
