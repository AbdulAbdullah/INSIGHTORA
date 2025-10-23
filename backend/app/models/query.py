"""
Query and analytics models for tracking user queries and AI processing
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class QueryStatus(PyEnum):
    """
    Query execution status
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryType(PyEnum):
    """
    Type of query
    """
    NATURAL_LANGUAGE = "natural_language"
    SQL = "sql"
    API = "api"
    FILE_ANALYSIS = "file_analysis"


class QueryHistory(Base):
    """
    Model for tracking all user queries and their results
    """
    __tablename__ = "query_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    
    # Query information
    query_type = Column(Enum(QueryType), nullable=False)
    natural_language = Column(Text, nullable=True)  # Original user question
    generated_sql = Column(Text, nullable=True)     # AI-generated SQL
    final_sql = Column(Text, nullable=True)         # Final executed SQL
    
    # Query context and metadata
    context = Column(JSON, default=dict)            # Additional context for AI
    query_parameters = Column(JSON, default=dict)   # Parameters used in query
    
    # Execution details
    status = Column(Enum(QueryStatus), default=QueryStatus.PENDING)
    execution_time = Column(Float, nullable=True)   # in seconds
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    # Results
    result_count = Column(Integer, nullable=True)   # Number of rows returned
    result_data = Column(JSON, nullable=True)       # Actual query results (limited)
    result_preview = Column(JSON, nullable=True)    # First few rows for display
    result_metadata = Column(JSON, default=dict)    # Column info, data types, etc.
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Performance metrics
    cache_hit = Column(Boolean, default=False)
    memory_usage = Column(Integer, nullable=True)   # in MB
    cpu_time = Column(Float, nullable=True)         # in seconds
    
    # User interaction
    user_rating = Column(Integer, nullable=True)    # 1-5 rating
    user_feedback = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # AI insights and recommendations
    ai_confidence = Column(Float, nullable=True)    # 0.0-1.0
    ai_explanation = Column(Text, nullable=True)    # How the SQL was generated
    suggested_improvements = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="queries")
    data_source = relationship("DataSource", back_populates="queries")
    visualizations = relationship("QueryVisualization", back_populates="query", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<QueryHistory(id={self.id}, type={self.query_type.value}, status={self.status.value})>"
    
    def to_dict(self):
        """Convert query to dictionary"""
        return {
            "id": self.id,
            "query_type": self.query_type.value,
            "natural_language": self.natural_language,
            "generated_sql": self.generated_sql,
            "status": self.status.value,
            "execution_time": self.execution_time,
            "result_count": self.result_count,
            "result_preview": self.result_preview,
            "error_message": self.error_message,
            "user_rating": self.user_rating,
            "is_favorite": self.is_favorite,
            "ai_confidence": self.ai_confidence,
            "ai_explanation": self.ai_explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class QueryVisualization(Base):
    """
    Model for storing visualization configurations generated from queries
    """
    __tablename__ = "query_visualizations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    query_id = Column(Integer, ForeignKey("query_history.id"), nullable=False)
    
    # Visualization configuration
    chart_type = Column(String(100), nullable=False)  # bar, line, pie, scatter, etc.
    chart_config = Column(JSON, default=dict)         # plotly/chart.js configuration
    chart_data = Column(JSON, default=dict)           # Processed data for chart
    
    # Display settings
    title = Column(String(255), nullable=True)
    subtitle = Column(String(500), nullable=True)
    width = Column(Integer, default=800)
    height = Column(Integer, default=400)
    
    # Styling and theme
    color_scheme = Column(String(100), default="default")
    theme = Column(String(50), default="light")
    custom_style = Column(JSON, default=dict)
    
    # Interactivity settings
    is_interactive = Column(Boolean, default=True)
    drill_down_enabled = Column(Boolean, default=False)
    export_enabled = Column(Boolean, default=True)
    
    # AI-generated insights
    ai_insights = Column(JSON, default=list)          # AI-generated insights about the chart
    suggested_chart_types = Column(JSON, default=list) # Alternative chart suggestions
    
    # Usage tracking
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    query = relationship("QueryHistory", back_populates="visualizations")
    
    def __repr__(self):
        return f"<QueryVisualization(id={self.id}, chart_type={self.chart_type})>"


class QueryCache(Base):
    """
    Model for caching query results to improve performance
    """
    __tablename__ = "query_cache"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Cache key (hash of query + parameters)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    
    # Original query information
    query_hash = Column(String(255), nullable=False)
    sql_query = Column(Text, nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    
    # Cached results
    result_data = Column(JSON, nullable=False)
    result_metadata = Column(JSON, default=dict)
    row_count = Column(Integer, nullable=False)
    
    # Cache metadata
    size_bytes = Column(Integer, nullable=False)
    compression_used = Column(Boolean, default=False)
    
    # Expiration and usage
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<QueryCache(id={self.id}, cache_key={self.cache_key[:20]}...)>"


class AIInsight(Base):
    """
    Model for storing AI-generated insights and recommendations
    """
    __tablename__ = "ai_insights"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    query_id = Column(Integer, ForeignKey("query_history.id"), nullable=True)
    
    # Insight details
    insight_type = Column(String(100), nullable=False)  # trend, anomaly, correlation, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # AI confidence and explanation
    confidence_score = Column(Float, nullable=False)    # 0.0-1.0
    explanation = Column(Text, nullable=True)
    evidence = Column(JSON, default=dict)              # Supporting data/metrics
    
    # Insight category and priority
    category = Column(String(100), nullable=True)      # business, technical, quality
    priority = Column(String(50), default="medium")    # low, medium, high, critical
    
    # Action recommendations
    recommended_actions = Column(JSON, default=list)
    potential_impact = Column(Text, nullable=True)
    
    # User interaction
    is_acknowledged = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    user_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AIInsight(id={self.id}, type={self.insight_type}, confidence={self.confidence_score})>"