"""
Query processing and AI analytics API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.query import QueryHistory, QueryStatus, QueryType
from app.models.data_source import DataSource
from app.utils.validators import QueryCreate, APIResponse, PaginationParams
from app.utils.exceptions import DataSourceNotFoundError, QueryExecutionError
from app.api.auth import get_current_user_dependency

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_query(
    query_data: QueryCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Create and execute a new query
    """
    try:
        # Validate data source if provided
        data_source = None
        if query_data.data_source_id:
            data_source = db.query(DataSource).filter(
                DataSource.id == query_data.data_source_id,
                DataSource.user_id == current_user.id
            ).first()
            
            if not data_source:
                raise DataSourceNotFoundError(query_data.data_source_id)
        
        # Create query history record
        query_record = QueryHistory(
            user_id=current_user.id,
            data_source_id=query_data.data_source_id,
            query_type=query_data.query_type,
            natural_language=query_data.natural_language,
            final_sql=query_data.sql_query,
            context=query_data.context,
            status=QueryStatus.PENDING
        )
        
        db.add(query_record)
        db.commit()
        db.refresh(query_record)
        
        # Process query based on type
        if query_data.query_type == QueryType.NATURAL_LANGUAGE:
            # This would integrate with LangChain/Groq for NL-to-SQL
            # For now, return a placeholder response
            result_data = {
                "message": "Natural language query processing will be implemented in Phase 3",
                "query": query_data.natural_language,
                "status": "pending_ai_processing"
            }
            
            query_record.ai_explanation = "Natural language processing will be implemented with LangChain"
            query_record.status = QueryStatus.PENDING
            
        elif query_data.query_type == QueryType.SQL:
            # This would execute SQL against the data source
            # For now, return a placeholder response
            result_data = {
                "message": "SQL query execution will be implemented with database connectors",
                "sql": query_data.sql_query,
                "status": "pending_execution"
            }
            
            query_record.status = QueryStatus.PENDING
        
        else:
            result_data = {
                "message": "Query type not yet supported",
                "status": "unsupported"
            }
            
            query_record.status = QueryStatus.FAILED
            query_record.error_message = "Unsupported query type"
        
        # Update query record
        db.commit()
        
        return APIResponse(
            success=True,
            message="Query created successfully",
            data={
                "query_id": query_record.id,
                "status": query_record.status.value,
                "result": result_data
            }
        )
        
    except DataSourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create query: {str(e)}"
        )


@router.get("/", response_model=APIResponse)
async def list_queries(
    pagination: PaginationParams = Depends(),
    query_type: Optional[QueryType] = None,
    status: Optional[QueryStatus] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List user's query history with filters and pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query
        query = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id)
        
        # Apply filters
        if query_type:
            query = query.filter(QueryHistory.query_type == query_type)
        
        if status:
            query = query.filter(QueryHistory.status == status)
        
        # Apply sorting
        if pagination.sort_by:
            if hasattr(QueryHistory, pagination.sort_by):
                column = getattr(QueryHistory, pagination.sort_by)
                if pagination.sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        else:
            # Default sort by creation date (newest first)
            query = query.order_by(QueryHistory.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        queries = query.offset(offset).limit(pagination.size).all()
        
        return APIResponse(
            success=True,
            message="Queries retrieved successfully",
            data=[q.to_dict() for q in queries],
            meta={
                "page": pagination.page,
                "size": pagination.size,
                "total": total,
                "pages": (total + pagination.size - 1) // pagination.size
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve queries: {str(e)}"
        )


@router.get("/{query_id}", response_model=APIResponse)
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get specific query by ID
    """
    try:
        query = db.query(QueryHistory).filter(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        return APIResponse(
            success=True,
            message="Query retrieved successfully",
            data=query.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve query: {str(e)}"
        )


@router.post("/{query_id}/execute", response_model=APIResponse)
async def execute_query(
    query_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Execute or re-execute a query
    """
    try:
        query = db.query(QueryHistory).filter(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        # Update query status
        query.status = QueryStatus.RUNNING
        db.commit()
        
        # This is where actual query execution would happen
        # For now, return placeholder response
        
        if query.query_type == QueryType.NATURAL_LANGUAGE:
            # Would integrate with LangChain here
            result = {
                "message": "Natural language query execution pending AI integration",
                "generated_sql": "SELECT * FROM table_name -- AI-generated SQL would appear here",
                "explanation": "The AI would explain how it interpreted your question"
            }
        elif query.query_type == QueryType.SQL:
            # Would execute SQL against data source here
            result = {
                "message": "SQL execution pending database connector integration",
                "rows_affected": 0,
                "execution_time": 0.0
            }
        else:
            result = {
                "message": "Query type not supported",
                "error": "Unsupported query type"
            }
        
        # Update query with results
        query.status = QueryStatus.COMPLETED if "error" not in result else QueryStatus.FAILED
        query.result_preview = result
        db.commit()
        
        return APIResponse(
            success=True,
            message="Query executed successfully",
            data={
                "query_id": query.id,
                "status": query.status.value,
                "result": result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Update query status to failed
        if 'query' in locals():
            query.status = QueryStatus.FAILED
            query.error_message = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@router.post("/{query_id}/favorite", response_model=APIResponse)
async def toggle_favorite_query(
    query_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Toggle favorite status of a query
    """
    try:
        query = db.query(QueryHistory).filter(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        # Toggle favorite status
        query.is_favorite = not query.is_favorite
        db.commit()
        
        return APIResponse(
            success=True,
            message=f"Query {'added to' if query.is_favorite else 'removed from'} favorites",
            data={"is_favorite": query.is_favorite}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update favorite status: {str(e)}"
        )


@router.delete("/{query_id}", response_model=APIResponse)
async def delete_query(
    query_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Delete a query from history
    """
    try:
        query = db.query(QueryHistory).filter(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        db.delete(query)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Query deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete query: {str(e)}"
        )


@router.get("/suggestions/chart-types", response_model=APIResponse)
async def suggest_chart_types(
    data_source_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get chart type suggestions for a data source
    """
    try:
        # Validate data source
        data_source = db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id
        ).first()
        
        if not data_source:
            raise DataSourceNotFoundError(data_source_id)
        
        # This would integrate with DataProcessor to analyze data and suggest charts
        # For now, return placeholder suggestions
        suggestions = [
            {
                "chart_type": "bar",
                "confidence": 0.9,
                "reason": "Categorical data detected",
                "description": "Bar chart for category comparison"
            },
            {
                "chart_type": "line",
                "confidence": 0.8,
                "reason": "Time series data available",
                "description": "Line chart for trend analysis"
            },
            {
                "chart_type": "scatter",
                "confidence": 0.7,
                "reason": "Multiple numeric columns",
                "description": "Scatter plot for correlation analysis"
            }
        ]
        
        return APIResponse(
            success=True,
            message="Chart type suggestions generated",
            data={"suggestions": suggestions}
        )
        
    except DataSourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )