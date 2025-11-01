"""
SQLAdmin configuration and ModelView classes for admin panel.
Provides a web-based interface for managing database models.
"""
from sqladmin import Admin, ModelView
from app.models.user import User
from app.models.group import Group
from app.models.membership import Membership
from app.models.channel import Channel
from app.models.message import Message, Reaction
from app.models.task import Task
from app.models.document import DocumentPage
from app.models.kanban import KanbanColumn, KanbanCard
from app.models.attachment import Attachment


class UserAdmin(ModelView, model=User):
    """Admin view for User model."""
    
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    # Columns to display in list view
    column_list = [
        User.id,
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
        User.created_at,
    ]
    
    # Columns searchable
    column_searchable_list = [User.username, User.email]
    
    # Columns that can be sorted
    column_sortable_list = [User.username, User.email, User.created_at]
    
    # Default sort
    column_default_sort = [(User.created_at, True)]
    
    # Fields to show in detail/edit forms
    column_details_exclude_list = [User.hashed_password]
    form_excluded_columns = [User.hashed_password, User.created_at, User.updated_at]
    
    # Make certain fields not editable
    form_edit_query_rel_fields = {
        "owned_groups": {"disabled": True},
        "memberships": {"disabled": True},
    }
    
    # Add custom labels
    column_labels = {
        "is_active": "Active",
        "is_superuser": "Admin",
        "avatar_url": "Avatar URL",
    }


class GroupAdmin(ModelView, model=Group):
    """Admin view for Group model."""
    
    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-users"
    
    column_list = [
        Group.id,
        Group.name,
        Group.owner_id,
        Group.created_at,
    ]
    
    column_searchable_list = [Group.name]
    column_sortable_list = [Group.name, Group.created_at]
    column_default_sort = [(Group.created_at, True)]
    
    # Show relationships
    column_details_list = [
        Group.id,
        Group.name,
        Group.owner,
        Group.created_at,
    ]
    
    form_excluded_columns = [Group.created_at, Group.updated_at]


class MembershipAdmin(ModelView, model=Membership):
    """Admin view for Membership model."""
    
    name = "Membership"
    name_plural = "Memberships"
    icon = "fa-solid fa-id-badge"
    
    column_list = [
        Membership.id,
        Membership.user_id,
        Membership.group_id,
        Membership.role,
        Membership.joined_at,
    ]
    
    column_searchable_list = [Membership.role]
    column_sortable_list = [Membership.role, Membership.joined_at]
    column_default_sort = [(Membership.joined_at, True)]
    
    # Filter by role
    column_filters = [Membership.role]
    
    form_excluded_columns = [Membership.joined_at]


class ChannelAdmin(ModelView, model=Channel):
    """Admin view for Channel model."""
    
    name = "Channel"
    name_plural = "Channels"
    icon = "fa-solid fa-hashtag"
    
    column_list = [
        Channel.id,
        Channel.name,
        Channel.type,
        Channel.group_id,
        Channel.created_at,
    ]
    
    column_searchable_list = [Channel.name]
    column_sortable_list = [Channel.name, Channel.type, Channel.created_at]
    column_default_sort = [(Channel.created_at, True)]
    
    # Filter by channel type
    column_filters = [Channel.type]
    
    form_excluded_columns = [Channel.created_at, Channel.updated_at]
    
    column_labels = {
        "type": "Channel Type",
    }


class MessageAdmin(ModelView, model=Message):
    """Admin view for Message model."""
    
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"
    
    column_list = [
        Message.id,
        Message.content,
        Message.user_id,
        Message.channel_id,
        Message.created_at,
    ]
    
    # Limit content display length
    column_formatters = {
        Message.content: lambda m, a: (m.content[:50] + '...') if len(m.content) > 50 else m.content
    }
    
    column_searchable_list = [Message.content]
    column_sortable_list = [Message.created_at]
    column_default_sort = [(Message.created_at, True)]
    
    # Filter by channel
    column_filters = [Message.channel_id, Message.user_id]
    
    form_excluded_columns = [Message.created_at]
    
    # Pagination
    page_size = 50
    page_size_options = [25, 50, 100, 200]


class ReactionAdmin(ModelView, model=Reaction):
    """Admin view for Reaction model."""
    
    name = "Reaction"
    name_plural = "Reactions"
    icon = "fa-solid fa-face-smile"
    
    column_list = [
        Reaction.id,
        Reaction.emoji,
        Reaction.user_id,
        Reaction.message_id,
    ]
    
    column_searchable_list = [Reaction.emoji]
    column_filters = [Reaction.emoji]
    
    page_size = 50


class TaskAdmin(ModelView, model=Task):
    """Admin view for Task model."""
    
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"
    
    column_list = [
        Task.id,
        Task.content,
        Task.is_completed,
        Task.channel_id,
        Task.assignee_id,
        Task.position,
        Task.created_at,
    ]
    
    column_searchable_list = [Task.content]
    column_sortable_list = [Task.is_completed, Task.position, Task.created_at]
    column_default_sort = [(Task.position, False)]
    
    # Filter by completion status
    column_filters = [Task.is_completed, Task.channel_id]
    
    form_excluded_columns = [Task.created_at, Task.updated_at]
    
    column_labels = {
        "is_completed": "Completed",
    }


class DocumentPageAdmin(ModelView, model=DocumentPage):
    """Admin view for DocumentPage model."""
    
    name = "Document"
    name_plural = "Documents"
    icon = "fa-solid fa-file-lines"
    
    column_list = [
        DocumentPage.id,
        DocumentPage.channel_id,
        DocumentPage.last_edited_by_id,
        DocumentPage.last_edited_at,
        DocumentPage.version,
        DocumentPage.created_at,
    ]
    
    # Limit content display
    column_formatters = {
        DocumentPage.content: lambda m, a: (m.content[:100] + '...') if m.content and len(m.content) > 100 else m.content
    }
    
    column_sortable_list = [DocumentPage.version, DocumentPage.last_edited_at, DocumentPage.created_at]
    column_default_sort = [(DocumentPage.last_edited_at, True)]
    
    column_filters = [DocumentPage.channel_id]
    
    form_excluded_columns = [DocumentPage.created_at, DocumentPage.updated_at]


class KanbanColumnAdmin(ModelView, model=KanbanColumn):
    """Admin view for KanbanColumn model."""
    
    name = "Kanban Column"
    name_plural = "Kanban Columns"
    icon = "fa-solid fa-columns"
    
    column_list = [
        KanbanColumn.id,
        KanbanColumn.title,
        KanbanColumn.channel_id,
        KanbanColumn.position,
        KanbanColumn.created_at,
    ]
    
    column_searchable_list = [KanbanColumn.title]
    column_sortable_list = [KanbanColumn.title, KanbanColumn.position, KanbanColumn.created_at]
    column_default_sort = [(KanbanColumn.position, False)]
    
    column_filters = [KanbanColumn.channel_id]
    
    form_excluded_columns = [KanbanColumn.created_at, KanbanColumn.updated_at]


class KanbanCardAdmin(ModelView, model=KanbanCard):
    """Admin view for KanbanCard model."""
    
    name = "Kanban Card"
    name_plural = "Kanban Cards"
    icon = "fa-solid fa-note-sticky"
    
    column_list = [
        KanbanCard.id,
        KanbanCard.content,
        KanbanCard.column_id,
        KanbanCard.position,
        KanbanCard.created_at,
    ]
    
    # Limit content display
    column_formatters = {
        KanbanCard.content: lambda m, a: (m.content[:50] + '...') if len(m.content) > 50 else m.content
    }
    
    column_searchable_list = [KanbanCard.content]
    column_sortable_list = [KanbanCard.position, KanbanCard.created_at]
    column_default_sort = [(KanbanCard.position, False)]
    
    column_filters = [KanbanCard.column_id]
    
    form_excluded_columns = [KanbanCard.created_at, KanbanCard.updated_at]


class AttachmentAdmin(ModelView, model=Attachment):
    """Admin view for Attachment model."""
    
    name = "Attachment"
    name_plural = "Attachments"
    icon = "fa-solid fa-paperclip"
    
    column_list = [
        Attachment.id,
        Attachment.filename,
        Attachment.file_size,
        Attachment.content_type,
        Attachment.message_id,
        Attachment.uploaded_by_id,
        Attachment.created_at,
    ]
    
    column_searchable_list = [Attachment.filename, Attachment.content_type]
    column_sortable_list = [Attachment.filename, Attachment.file_size, Attachment.created_at]
    column_default_sort = [(Attachment.created_at, True)]
    
    column_filters = [Attachment.content_type, Attachment.message_id]
    
    form_excluded_columns = [Attachment.created_at]
    
    # Format file size
    column_formatters = {
        Attachment.file_size: lambda m, a: f"{m.file_size / 1024:.2f} KB" if m.file_size else "0 KB"
    }


def setup_admin(app, engine):
    """
    Setup and configure SQLAdmin with all model views.
    
    Args:
        app: FastAPI application instance
        engine: SQLAlchemy async engine
    
    Returns:
        Admin instance
    """
    from sqladmin.authentication import AuthenticationBackend
    from starlette.requests import Request
    from starlette.responses import RedirectResponse
    from app.core.security import verify_password
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    
    class AdminAuth(AuthenticationBackend):
        """
        Custom authentication backend for SQLAdmin.
        Only allows users with is_superuser=True to access admin panel.
        """
        
        async def login(self, request: Request) -> bool:
            """Handle admin login."""
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
            
            # Get database session
            from app.db.session import async_session_maker
            async with async_session_maker() as session:
                # Find user by username
                result = await session.execute(
                    select(User).where(User.username == username)
                )
                user = result.scalar_one_or_none()
                
                # Verify user exists, is active, is superuser, and password is correct
                if user and user.is_active and user.is_superuser:
                    if verify_password(password, user.hashed_password):
                        # Store user ID in session
                        request.session.update({"user_id": user.id})
                        return True
            
            return False
        
        async def logout(self, request: Request) -> bool:
            """Handle admin logout."""
            request.session.clear()
            return True
        
        async def authenticate(self, request: Request) -> bool:
            """Check if user is authenticated."""
            user_id = request.session.get("user_id")
            
            if not user_id:
                return False
            
            # Verify user still exists and is superuser
            from app.db.session import async_session_maker
            async with async_session_maker() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if user and user.is_active and user.is_superuser:
                    return True
            
            return False
    
    # Create authentication backend
    authentication_backend = AdminAuth(secret_key="your-secret-key-change-in-production")
    
    # Create admin instance
    admin = Admin(
        app=app,
        engine=engine,
        title="Collaboration Platform Admin",
        authentication_backend=authentication_backend,
        base_url="/admin",
    )
    
    # Add all model views
    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(MembershipAdmin)
    admin.add_view(ChannelAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(ReactionAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(DocumentPageAdmin)
    admin.add_view(KanbanColumnAdmin)
    admin.add_view(KanbanCardAdmin)
    admin.add_view(AttachmentAdmin)
    
    return admin
