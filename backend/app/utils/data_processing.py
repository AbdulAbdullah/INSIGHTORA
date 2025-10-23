"""
Data processing utilities using pandas for analytics and transformations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging
from io import StringIO, BytesIO
import hashlib
from datetime import datetime

from app.utils.exceptions import DataProcessingError, FileProcessingError

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Main data processing class for handling various data operations
    """
    
    @staticmethod
    def read_csv_file(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read CSV file with error handling and type inference
        """
        try:
            # Default parameters for robust CSV reading
            default_params = {
                'encoding': 'utf-8',
                'on_bad_lines': 'skip',
                'low_memory': False,
                'dtype': str,  # Read everything as string first
                'na_values': ['', 'NULL', 'null', 'None', 'none', 'N/A', 'n/a', '#N/A']
            }
            default_params.update(kwargs)
            
            df = pd.read_csv(file_path, **default_params)
            
            # Auto-detect and convert data types
            df = DataProcessor.auto_convert_types(df)
            
            logger.info(f"Successfully read CSV file: {file_path}, shape: {df.shape}")
            return df
            
        except Exception as e:
            raise FileProcessingError(
                f"Failed to read CSV file: {str(e)}",
                error_code="CSV_READ_ERROR",
                details={"file_path": file_path, "error": str(e)}
            )
    
    @staticmethod
    def read_excel_file(file_path: str, sheet_name: Union[str, int, None] = None) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Read Excel file with support for multiple sheets
        """
        try:
            if sheet_name is None:
                # Read all sheets
                dfs = pd.read_excel(file_path, sheet_name=None, dtype=str)
                # Convert types for each sheet
                for sheet, df in dfs.items():
                    dfs[sheet] = DataProcessor.auto_convert_types(df)
                logger.info(f"Successfully read Excel file: {file_path}, sheets: {list(dfs.keys())}")
                return dfs
            else:
                # Read specific sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
                df = DataProcessor.auto_convert_types(df)
                logger.info(f"Successfully read Excel sheet '{sheet_name}': {file_path}, shape: {df.shape}")
                return df
                
        except Exception as e:
            raise FileProcessingError(
                f"Failed to read Excel file: {str(e)}",
                error_code="EXCEL_READ_ERROR",
                details={"file_path": file_path, "sheet_name": sheet_name, "error": str(e)}
            )
    
    @staticmethod
    def read_json_file(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read JSON file and convert to DataFrame
        """
        try:
            df = pd.read_json(file_path, **kwargs)
            logger.info(f"Successfully read JSON file: {file_path}, shape: {df.shape}")
            return df
            
        except Exception as e:
            raise FileProcessingError(
                f"Failed to read JSON file: {str(e)}",
                error_code="JSON_READ_ERROR",
                details={"file_path": file_path, "error": str(e)}
            )
    
    @staticmethod
    def auto_convert_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Automatically detect and convert data types for optimal performance
        """
        try:
            for column in df.columns:
                # Skip if already numeric
                if pd.api.types.is_numeric_dtype(df[column]):
                    continue
                
                # Try to convert to numeric
                numeric_series = pd.to_numeric(df[column], errors='coerce')
                
                # If conversion was successful for most values (>50%), use it
                if numeric_series.notna().sum() / len(df) > 0.5:
                    # Check if it should be integer or float
                    if numeric_series.notna().all() and (numeric_series % 1 == 0).all():
                        df[column] = numeric_series.astype('Int64')  # Nullable integer
                    else:
                        df[column] = numeric_series
                    continue
                
                # Try to convert to datetime
                try:
                    datetime_series = pd.to_datetime(df[column], errors='coerce', infer_datetime_format=True)
                    if datetime_series.notna().sum() / len(df) > 0.5:
                        df[column] = datetime_series
                        continue
                except:
                    pass
                
                # Try to convert to boolean
                if df[column].dropna().isin([True, False, 'True', 'False', 'true', 'false', 1, 0, '1', '0']).all():
                    df[column] = df[column].map({
                        'True': True, 'true': True, '1': True, 1: True,
                        'False': False, 'false': False, '0': False, 0: False
                    })
                    continue
                
                # Keep as string but optimize memory
                df[column] = df[column].astype('string')
            
            return df
            
        except Exception as e:
            logger.warning(f"Error in auto type conversion: {str(e)}")
            return df
    
    @staticmethod
    def get_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data profile with statistics and quality metrics
        """
        try:
            profile = {
                "basic_info": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "memory_usage": df.memory_usage(deep=True).sum(),
                    "dtypes": df.dtypes.astype(str).to_dict()
                },
                "column_profiles": {},
                "data_quality": {
                    "missing_values": df.isnull().sum().to_dict(),
                    "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
                    "duplicate_rows": df.duplicated().sum(),
                    "duplicate_percentage": df.duplicated().sum() / len(df) * 100
                },
                "sample_data": df.head(10).to_dict('records')
            }
            
            # Generate profile for each column
            for column in df.columns:
                col_profile = DataProcessor.get_column_profile(df[column])
                profile["column_profiles"][column] = col_profile
            
            return profile
            
        except Exception as e:
            raise DataProcessingError(
                f"Failed to generate data profile: {str(e)}",
                error_code="DATA_PROFILE_ERROR",
                details={"error": str(e)}
            )
    
    @staticmethod
    def get_column_profile(series: pd.Series) -> Dict[str, Any]:
        """
        Generate detailed profile for a single column
        """
        profile = {
            "name": series.name,
            "dtype": str(series.dtype),
            "count": len(series),
            "non_null_count": series.count(),
            "null_count": series.isnull().sum(),
            "null_percentage": series.isnull().sum() / len(series) * 100,
            "unique_count": series.nunique(),
            "unique_percentage": series.nunique() / len(series) * 100
        }
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(series):
            profile.update({
                "min": series.min() if series.count() > 0 else None,
                "max": series.max() if series.count() > 0 else None,
                "mean": series.mean() if series.count() > 0 else None,
                "median": series.median() if series.count() > 0 else None,
                "std": series.std() if series.count() > 0 else None,
                "quartiles": series.quantile([0.25, 0.5, 0.75]).to_dict() if series.count() > 0 else {}
            })
        
        elif pd.api.types.is_datetime64_any_dtype(series):
            profile.update({
                "min_date": series.min().isoformat() if series.count() > 0 else None,
                "max_date": series.max().isoformat() if series.count() > 0 else None,
                "date_range_days": (series.max() - series.min()).days if series.count() > 0 else None
            })
        
        else:
            # String/categorical data
            value_counts = series.value_counts().head(10)
            profile.update({
                "most_common": value_counts.to_dict(),
                "avg_length": series.astype(str).str.len().mean() if series.count() > 0 else None,
                "max_length": series.astype(str).str.len().max() if series.count() > 0 else None,
                "min_length": series.astype(str).str.len().min() if series.count() > 0 else None
            })
        
        return profile
    
    @staticmethod
    def detect_relationships(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect potential relationships between columns
        """
        relationships = []
        
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            # Calculate correlations for numeric columns
            if len(numeric_columns) > 1:
                corr_matrix = df[numeric_columns].corr()
                
                for i, col1 in enumerate(numeric_columns):
                    for j, col2 in enumerate(numeric_columns[i+1:], i+1):
                        correlation = corr_matrix.loc[col1, col2]
                        
                        if abs(correlation) > 0.5:  # Strong correlation threshold
                            relationships.append({
                                "type": "correlation",
                                "column1": col1,
                                "column2": col2,
                                "strength": abs(correlation),
                                "direction": "positive" if correlation > 0 else "negative"
                            })
            
            # Detect potential foreign key relationships
            for col1 in df.columns:
                for col2 in df.columns:
                    if col1 != col2:
                        # Check if all values in col1 exist in col2 (potential FK)
                        if df[col1].dropna().isin(df[col2].dropna()).all():
                            relationships.append({
                                "type": "foreign_key",
                                "foreign_key": col1,
                                "primary_key": col2,
                                "match_percentage": 100
                            })
            
            return relationships
            
        except Exception as e:
            logger.warning(f"Error detecting relationships: {str(e)}")
            return []
    
    @staticmethod
    def suggest_chart_types(df: pd.DataFrame, target_column: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Suggest appropriate chart types based on data characteristics
        """
        suggestions = []
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Time series charts
            if datetime_cols and numeric_cols:
                suggestions.append({
                    "chart_type": "line",
                    "confidence": 0.9,
                    "reason": "Time series data detected",
                    "x_axis": datetime_cols[0],
                    "y_axis": numeric_cols[0],
                    "description": "Line chart for time series analysis"
                })
            
            # Bar charts for categorical vs numeric
            if categorical_cols and numeric_cols:
                suggestions.append({
                    "chart_type": "bar", 
                    "confidence": 0.8,
                    "reason": "Categorical and numeric columns available",
                    "x_axis": categorical_cols[0],
                    "y_axis": numeric_cols[0],
                    "description": "Bar chart for category comparison"
                })
            
            # Scatter plots for numeric relationships
            if len(numeric_cols) >= 2:
                suggestions.append({
                    "chart_type": "scatter",
                    "confidence": 0.7,
                    "reason": "Multiple numeric columns for correlation analysis",
                    "x_axis": numeric_cols[0],
                    "y_axis": numeric_cols[1],
                    "description": "Scatter plot to analyze correlation"
                })
            
            # Pie charts for categorical distributions
            if categorical_cols:
                suggestions.append({
                    "chart_type": "pie",
                    "confidence": 0.6,
                    "reason": "Categorical data suitable for distribution analysis",
                    "category": categorical_cols[0],
                    "description": "Pie chart for category distribution"
                })
            
            # Histogram for numeric distributions
            if numeric_cols:
                suggestions.append({
                    "chart_type": "histogram",
                    "confidence": 0.7,
                    "reason": "Numeric data suitable for distribution analysis",
                    "column": numeric_cols[0],
                    "description": "Histogram to show data distribution"
                })
            
            return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.warning(f"Error suggesting chart types: {str(e)}")
            return []
    
    @staticmethod
    def generate_cache_key(query: str, parameters: Dict[str, Any] = None) -> str:
        """
        Generate cache key for query results
        """
        if parameters is None:
            parameters = {}
        
        # Create a consistent string representation
        cache_string = f"{query}_{json.dumps(parameters, sort_keys=True)}"
        
        # Generate hash
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @staticmethod
    def clean_data(df: pd.DataFrame, operations: List[str] = None) -> pd.DataFrame:
        """
        Apply data cleaning operations
        """
        if operations is None:
            operations = ["remove_duplicates", "handle_missing", "standardize_text"]
        
        cleaned_df = df.copy()
        
        try:
            for operation in operations:
                if operation == "remove_duplicates":
                    cleaned_df = cleaned_df.drop_duplicates()
                
                elif operation == "handle_missing":
                    # Fill missing values based on column type
                    for column in cleaned_df.columns:
                        if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                            cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].median())
                        else:
                            cleaned_df[column] = cleaned_df[column].fillna("Unknown")
                
                elif operation == "standardize_text":
                    # Standardize text columns
                    text_columns = cleaned_df.select_dtypes(include=['object', 'string']).columns
                    for column in text_columns:
                        cleaned_df[column] = cleaned_df[column].astype(str).str.strip().str.title()
            
            logger.info(f"Data cleaning completed. Original shape: {df.shape}, Cleaned shape: {cleaned_df.shape}")
            return cleaned_df
            
        except Exception as e:
            raise DataProcessingError(
                f"Failed to clean data: {str(e)}",
                error_code="DATA_CLEANING_ERROR",
                details={"operations": operations, "error": str(e)}
            )
    
    @staticmethod
    def sample_data(df: pd.DataFrame, sample_size: int = 1000, method: str = "random") -> pd.DataFrame:
        """
        Sample data for performance optimization
        """
        try:
            if len(df) <= sample_size:
                return df
            
            if method == "random":
                return df.sample(n=sample_size, random_state=42)
            elif method == "systematic":
                step = len(df) // sample_size
                return df.iloc[::step][:sample_size]
            elif method == "stratified" and len(df.columns) > 0:
                # Simple stratified sampling on first categorical column
                categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns
                if len(categorical_cols) > 0:
                    return df.groupby(categorical_cols[0]).apply(
                        lambda x: x.sample(min(len(x), sample_size // df[categorical_cols[0]].nunique()))
                    ).reset_index(drop=True)
                else:
                    return df.sample(n=sample_size, random_state=42)
            else:
                return df.sample(n=sample_size, random_state=42)
                
        except Exception as e:
            logger.warning(f"Error sampling data: {str(e)}. Returning original data.")
            return df