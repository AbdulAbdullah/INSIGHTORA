"""
Data source management API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.data_source import DataSource, DataTable, DataColumn
from app.utils.validators import DataSourceCreate, APIResponse, PaginationParams
from app.utils.exceptions import DataSourceNotFoundError
from app.utils.data_processing import DataProcessor
from app.api.auth import get_current_user_dependency

router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_data_source(
    data_source_data: DataSourceCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Create a new data source
    """
    try:
        # Create new data source
        new_data_source = DataSource(
            user_id=current_user.id,
            name=data_source_data.name,
            description=data_source_data.description,
            type=data_source_data.type,
            connection_config=data_source_data.connection_config
        )
        
        db.add(new_data_source)
        db.commit()
        db.refresh(new_data_source)
        
        return APIResponse(
            success=True,
            message="Data source created successfully",
            data=new_data_source.to_dict()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create data source: {str(e)}"
        )


@router.get("/", response_model=APIResponse)
async def list_data_sources(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List user's data sources with pagination
    """
    try:
        # Calculate offset
        offset = (pagination.page - 1) * pagination.size
        
        # Query data sources
        query = db.query(DataSource).filter(DataSource.user_id == current_user.id)
        
        # Apply sorting
        if pagination.sort_by:
            if hasattr(DataSource, pagination.sort_by):
                column = getattr(DataSource, pagination.sort_by)
                if pagination.sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        data_sources = query.offset(offset).limit(pagination.size).all()
        
        return APIResponse(
            success=True,
            message="Data sources retrieved successfully",
            data=[ds.to_dict() for ds in data_sources],
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
            detail=f"Failed to retrieve data sources: {str(e)}"
        )


@router.get("/{data_source_id}", response_model=APIResponse)
async def get_data_source(
    data_source_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get specific data source by ID
    """
    try:
        data_source = db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id
        ).first()
        
        if not data_source:
            raise DataSourceNotFoundError(data_source_id)
        
        return APIResponse(
            success=True,
            message="Data source retrieved successfully",
            data=data_source.to_dict()
        )
        
    except DataSourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve data source: {str(e)}"
        )


@router.post("/upload", response_model=APIResponse)
async def upload_file(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Upload and process a data file (CSV, Excel, JSON)
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file based on type
        try:
            if file_extension == '.csv':
                df = DataProcessor.read_csv_file(file_path)
                data_source_type = "csv"
            elif file_extension in ['.xlsx', '.xls']:
                df = DataProcessor.read_excel_file(file_path)
                if isinstance(df, dict):
                    # Multiple sheets, use first sheet
                    df = list(df.values())[0]
                data_source_type = "excel"
            elif file_extension == '.json':
                df = DataProcessor.read_json_file(file_path)
                data_source_type = "json"
            
            # Generate data profile
            profile = DataProcessor.get_data_profile(df)
            
            # Create data source record
            data_source = DataSource(
                user_id=current_user.id,
                name=name or file.filename,
                description=description,
                type=data_source_type,
                file_path=file_path,
                file_size=len(content),
                file_mime_type=file.content_type,
                original_filename=file.filename,
                row_count=len(df),
                column_count=len(df.columns),
                schema_cache=profile
            )
            
            db.add(data_source)
            db.commit()
            db.refresh(data_source)
            
            return APIResponse(
                success=True,
                message="File uploaded and processed successfully",
                data={
                    "data_source": data_source.to_dict(),
                    "profile": profile
                }
            )
            
        except Exception as processing_error:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process file: {str(processing_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{data_source_id}/preview", response_model=APIResponse)
async def preview_data_source(
    data_source_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Preview data from a data source
    """
    try:
        data_source = db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id
        ).first()
        
        if not data_source:
            raise DataSourceNotFoundError(data_source_id)
        
        # Load data based on source type
        if data_source.type in ["csv", "excel", "json"] and data_source.file_path:
            if data_source.type == "csv":
                df = DataProcessor.read_csv_file(data_source.file_path)
            elif data_source.type == "excel":
                df = DataProcessor.read_excel_file(data_source.file_path)
                if isinstance(df, dict):
                    df = list(df.values())[0]
            elif data_source.type == "json":
                df = DataProcessor.read_json_file(data_source.file_path)
            
            # Limit preview data
            preview_df = df.head(limit)
            
            return APIResponse(
                success=True,
                message="Data preview retrieved successfully",
                data={
                    "columns": list(df.columns),
                    "data": preview_df.to_dict('records'),
                    "total_rows": len(df),
                    "preview_rows": len(preview_df)
                }
            )
        else:
            # For database sources, would implement database query here
            return APIResponse(
                success=True,
                message="Preview not available for this data source type",
                data={"columns": [], "data": []}
            )
            
    except DataSourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview data: {str(e)}"
        )


@router.delete("/{data_source_id}", response_model=APIResponse)
async def delete_data_source(
    data_source_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Delete a data source
    """
    try:
        data_source = db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.user_id == current_user.id
        ).first()
        
        if not data_source:
            raise DataSourceNotFoundError(data_source_id)
        
        # Delete associated file if exists
        if data_source.file_path and os.path.exists(data_source.file_path):
            os.remove(data_source.file_path)
        
        # Delete from database
        db.delete(data_source)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Data source deleted successfully"
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
            detail=f"Failed to delete data source: {str(e)}"
        )