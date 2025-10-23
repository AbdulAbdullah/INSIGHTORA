"""
Dashboard and widget models for building interactive dashboards
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class DashboardStatus(PyEnum):
    """
    Dashboard status enumeration
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SHARED = "shared"


class WidgetType(PyEnum):
    """
    Widget type enumeration
    """
    CHART = "chart"
    TABLE = "table"
    METRIC = "metric"
    TEXT = "text"
    IMAGE = "image"
    FILTER = "filter"
    MAP = "map"
    IFRAME = "iframe"


class Dashboard(Base):
    """
    Dashboard model for organizing and displaying multiple widgets
    """
    __tablename__ = "dashboards"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Layout and design
    layout_config = Column(JSON, default=dict)        # Grid layout configuration
    theme = Column(String(50), default="default")      # Theme name
    custom_css = Column(Text, nullable=True)           # Custom CSS styles
    
    # Display settings
    width = Column(Integer, default=1200)
    height = Column(Integer, nullable=True)
    is_responsive = Column(Boolean, default=True)
    auto_refresh = Column(Boolean, default=False)
    refresh_interval = Column(Integer, nullable=True)  # in seconds
    
    # Access control
    status = Column(Enum(DashboardStatus), default=DashboardStatus.DRAFT)
    is_public = Column(Boolean, default=False)
    password_protected = Column(Boolean, default=False)
    access_password = Column(String(255), nullable=True)  # hashed
    
    # Sharing and collaboration
    share_token = Column(String(255), unique=True, nullable=True)
    allowed_users = Column(JSON, default=list)         # List of user IDs with access
    allowed_roles = Column(JSON, default=list)         # List of roles with access
    
    # Usage analytics
    view_count = Column(Integer, default=0)
    unique_viewers = Column(JSON, default=list)        # List of user IDs who viewed
    last_viewed = Column(DateTime, nullable=True)
    
    # Performance settings
    cache_enabled = Column(Boolean, default=True)
    cache_duration = Column(Integer, default=300)      # in seconds
    
    # Export and integration
    export_formats = Column(JSON, default=list)        # Supported export formats
    webhook_url = Column(String(500), nullable=True)   # Webhook for updates
    
    # Metadata
    tags = Column(JSON, default=list)                  # Tags for organization
    category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")
    comments = relationship("DashboardComment", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dashboard(id={self.id}, title={self.title}, status={self.status.value})>"
    
    def to_dict(self):
        """Convert dashboard to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "layout_config": self.layout_config,
            "theme": self.theme,
            "width": self.width,
            "height": self.height,
            "is_responsive": self.is_responsive,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "status": self.status.value,
            "is_public": self.is_public,
            "view_count": self.view_count,
            "tags": self.tags,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }


class DashboardWidget(Base):
    """
    Individual widget within a dashboard
    """
    __tablename__ = "dashboard_widgets"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    query_id = Column(Integer, ForeignKey("query_history.id"), nullable=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    
    # Widget identification
    widget_type = Column(Enum(WidgetType), nullable=False)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)
    
    # Layout and positioning
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)                 # Grid units
    height = Column(Integer, default=3)                # Grid units
    z_index = Column(Integer, default=1)
    
    # Widget configuration
    config = Column(JSON, default=dict)               # Widget-specific configuration
    data_config = Column(JSON, default=dict)          # Data binding configuration
    style_config = Column(JSON, default=dict)         # Styling configuration
    
    # Data and refresh
    cached_data = Column(JSON, nullable=True)         # Cached widget data
    data_last_updated = Column(DateTime, nullable=True)
    auto_refresh = Column(Boolean, default=False)
    refresh_interval = Column(Integer, nullable=True) # in seconds
    
    # Interactivity
    is_interactive = Column(Boolean, default=True)
    click_action = Column(JSON, default=dict)         # Action on click
    drill_down_config = Column(JSON, default=dict)    # Drill-down configuration
    
    # Conditional formatting and alerts
    alert_conditions = Column(JSON, default=list)     # Alert rules
    conditional_formatting = Column(JSON, default=list)
    
    # Visibility and permissions
    is_visible = Column(Boolean, default=True)
    visibility_conditions = Column(JSON, default=list) # Conditional visibility
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")
    query = relationship("QueryHistory")
    data_source = relationship("DataSource")
    
    def __repr__(self):
        return f"<DashboardWidget(id={self.id}, type={self.widget_type.value}, title={self.title})>"
    
    def to_dict(self):
        """Convert widget to dictionary"""
        return {
            "id": self.id,
            "widget_type": self.widget_type.value,
            "title": self.title,
            "subtitle": self.subtitle,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "width": self.width,
            "height": self.height,
            "config": self.config,
            "data_config": self.data_config,
            "style_config": self.style_config,
            "is_interactive": self.is_interactive,
            "is_visible": self.is_visible,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DashboardComment(Base):
    """
    Comments and annotations on dashboards for collaboration
    """
    __tablename__ = "dashboard_comments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("dashboard_comments.id"), nullable=True)  # For replies
    
    # Comment content
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="comment")  # comment, suggestion, issue
    
    # Position (for positioned comments)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    widget_id = Column(Integer, ForeignKey("dashboard_widgets.id"), nullable=True)
    
    # Status and resolution
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Metadata
    context_metadata = Column(JSON, default=dict)             # Additional context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dashboard = relationship("Dashboard", back_populates="comments")
    author = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    replies = relationship("DashboardComment", remote_side=[id])
    widget = relationship("DashboardWidget")
    
    def __repr__(self):
        return f"<DashboardComment(id={self.id}, type={self.comment_type}, resolved={self.is_resolved})>"


class DashboardTemplate(Base):
    """
    Pre-built dashboard templates for quick setup
    """
    __tablename__ = "dashboard_templates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Template information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)      # sales, marketing, finance, etc.
    
    # Template configuration
    template_config = Column(JSON, nullable=False)    # Full dashboard configuration
    required_data_sources = Column(JSON, default=list) # Required data source types
    sample_data = Column(JSON, default=dict)          # Sample data for preview
    
    # Usage and popularity
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)
    
    # Template metadata
    tags = Column(JSON, default=list)
    difficulty_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    estimated_setup_time = Column(Integer, nullable=True)      # in minutes
    
    # Template status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Author information
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_official = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User")
    
    def __repr__(self):
        return f"<DashboardTemplate(id={self.id}, name={self.name}, category={self.category})>"