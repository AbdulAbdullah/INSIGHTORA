"""
Dashboard management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.dashboard import Dashboard, DashboardWidget, DashboardStatus
from app.utils.validators import DashboardCreate, WidgetCreate, APIResponse, PaginationParams
from app.api.auth import get_current_user_dependency

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Create a new dashboard
    """
    try:
        # Create new dashboard
        new_dashboard = Dashboard(
            user_id=current_user.id,
            title=dashboard_data.title,
            description=dashboard_data.description,
            layout_config=dashboard_data.layout_config,
            theme=dashboard_data.theme,
            is_public=dashboard_data.is_public,
            tags=dashboard_data.tags,
            status=DashboardStatus.DRAFT
        )
        
        db.add(new_dashboard)
        db.commit()
        db.refresh(new_dashboard)
        
        return APIResponse(
            success=True,
            message="Dashboard created successfully",
            data=new_dashboard.to_dict()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dashboard: {str(e)}"
        )


@router.get("/", response_model=APIResponse)
async def list_dashboards(
    pagination: PaginationParams = Depends(),
    status: Optional[DashboardStatus] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List user's dashboards with pagination and filters
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Build query
        query = db.query(Dashboard).filter(Dashboard.user_id == current_user.id)
        
        # Apply status filter
        if status:
            query = query.filter(Dashboard.status == status)
        
        # Apply sorting
        if pagination.sort_by:
            if hasattr(Dashboard, pagination.sort_by):
                column = getattr(Dashboard, pagination.sort_by)
                if pagination.sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        else:
            # Default sort by updated date (newest first)
            query = query.order_by(Dashboard.updated_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        dashboards = query.offset(offset).limit(pagination.size).all()
        
        return APIResponse(
            success=True,
            message="Dashboards retrieved successfully",
            data=[d.to_dict() for d in dashboards],
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
            detail=f"Failed to retrieve dashboards: {str(e)}"
        )


@router.get("/{dashboard_id}", response_model=APIResponse)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get specific dashboard by ID with all widgets
    """
    try:
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Get dashboard with widgets
        dashboard_data = dashboard.to_dict()
        
        # Get widgets
        widgets = db.query(DashboardWidget).filter(
            DashboardWidget.dashboard_id == dashboard_id
        ).all()
        
        dashboard_data["widgets"] = [w.to_dict() for w in widgets]
        
        # Update view count
        dashboard.view_count += 1
        db.commit()
        
        return APIResponse(
            success=True,
            message="Dashboard retrieved successfully",
            data=dashboard_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@router.put("/{dashboard_id}", response_model=APIResponse)
async def update_dashboard(
    dashboard_id: int,
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Update an existing dashboard
    """
    try:
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Update dashboard fields
        dashboard.title = dashboard_data.title
        dashboard.description = dashboard_data.description
        dashboard.layout_config = dashboard_data.layout_config
        dashboard.theme = dashboard_data.theme
        dashboard.is_public = dashboard_data.is_public
        dashboard.tags = dashboard_data.tags
        
        db.commit()
        db.refresh(dashboard)
        
        return APIResponse(
            success=True,
            message="Dashboard updated successfully",
            data=dashboard.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dashboard: {str(e)}"
        )


@router.post("/{dashboard_id}/widgets", response_model=APIResponse)
async def add_widget_to_dashboard(
    dashboard_id: int,
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Add a new widget to a dashboard
    """
    try:
        # Verify dashboard ownership
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Create new widget
        new_widget = DashboardWidget(
            dashboard_id=dashboard_id,
            widget_type=widget_data.widget_type,
            title=widget_data.title,
            subtitle=widget_data.subtitle,
            position_x=widget_data.position_x,
            position_y=widget_data.position_y,
            width=widget_data.width,
            height=widget_data.height,
            config=widget_data.config,
            query_id=widget_data.query_id,
            data_source_id=widget_data.data_source_id
        )
        
        db.add(new_widget)
        db.commit()
        db.refresh(new_widget)
        
        return APIResponse(
            success=True,
            message="Widget added to dashboard successfully",
            data=new_widget.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add widget: {str(e)}"
        )


@router.put("/{dashboard_id}/widgets/{widget_id}", response_model=APIResponse)
async def update_dashboard_widget(
    dashboard_id: int,
    widget_id: int,
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Update a widget in a dashboard
    """
    try:
        # Verify dashboard ownership
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Find widget
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.dashboard_id == dashboard_id
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        # Update widget
        widget.widget_type = widget_data.widget_type
        widget.title = widget_data.title
        widget.subtitle = widget_data.subtitle
        widget.position_x = widget_data.position_x
        widget.position_y = widget_data.position_y
        widget.width = widget_data.width
        widget.height = widget_data.height
        widget.config = widget_data.config
        widget.query_id = widget_data.query_id
        widget.data_source_id = widget_data.data_source_id
        
        db.commit()
        db.refresh(widget)
        
        return APIResponse(
            success=True,
            message="Widget updated successfully",
            data=widget.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update widget: {str(e)}"
        )


@router.delete("/{dashboard_id}/widgets/{widget_id}", response_model=APIResponse)
async def delete_dashboard_widget(
    dashboard_id: int,
    widget_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Delete a widget from a dashboard
    """
    try:
        # Verify dashboard ownership
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Find and delete widget
        widget = db.query(DashboardWidget).filter(
            DashboardWidget.id == widget_id,
            DashboardWidget.dashboard_id == dashboard_id
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )
        
        db.delete(widget)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Widget deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete widget: {str(e)}"
        )


@router.post("/{dashboard_id}/publish", response_model=APIResponse)
async def publish_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Publish a dashboard (change status from draft to published)
    """
    try:
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Update status to published
        dashboard.status = DashboardStatus.PUBLISHED
        dashboard.published_at = func.now()
        db.commit()
        
        return APIResponse(
            success=True,
            message="Dashboard published successfully",
            data={"status": dashboard.status.value}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish dashboard: {str(e)}"
        )


@router.delete("/{dashboard_id}", response_model=APIResponse)
async def delete_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Delete a dashboard and all its widgets
    """
    try:
        dashboard = db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == current_user.id
        ).first()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Delete dashboard (widgets will be deleted due to cascade)
        db.delete(dashboard)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Dashboard deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dashboard: {str(e)}"
        )