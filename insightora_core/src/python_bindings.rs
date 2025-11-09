// Python-Rust Interface using PyO3
// Provides Python bindings for all Rust performance modules

use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyMemoryError, PyTypeError, PyValueError};
use std::sync::{Arc, RwLock};
use once_cell::sync::Lazy;

/// Global configuration for the Rust module
static GLOBAL_CONFIG: Lazy<Arc<RwLock<RustConfig>>> = Lazy::new(|| {
    Arc::new(RwLock::new(RustConfig::default()))
});

/// Track if thread pool has been initialized
static THREAD_POOL_INITIALIZED: Lazy<Arc<RwLock<bool>>> = Lazy::new(|| {
    Arc::new(RwLock::new(false))
});

/// Configuration structure for Rust module
#[derive(Debug, Clone)]
pub struct RustConfig {
    pub thread_count: usize,
    pub chunk_size: usize,
    pub memory_limit_mb: usize,
    pub enable_simd: bool,
    pub cache_size: usize,
}

impl Default for RustConfig {
    fn default() -> Self {
        Self {
            thread_count: num_cpus::get(),
            chunk_size: 100_000,
            memory_limit_mb: 4096,
            enable_simd: true,
            cache_size: 1000,
        }
    }
}

/// Configure the Rust module with custom settings
/// 
/// # Arguments
/// * `thread_count` - Number of threads to use (0 = auto-detect)
/// * `chunk_size` - Size of data chunks for parallel processing
/// * `memory_limit_mb` - Maximum memory usage in megabytes
/// * `enable_simd` - Enable SIMD optimizations
/// * `cache_size` - Size of internal caches
/// 
/// # Example
/// ```python
/// import insightora_core
/// insightora_core.configure(thread_count=8, memory_limit_mb=8192)
/// ```
#[pyfunction]
#[pyo3(signature = (thread_count=None, chunk_size=None, memory_limit_mb=None, enable_simd=None, cache_size=None))]
pub fn configure(
    thread_count: Option<usize>,
    chunk_size: Option<usize>,
    memory_limit_mb: Option<usize>,
    enable_simd: Option<bool>,
    cache_size: Option<usize>,
) -> PyResult<()> {
    let mut config = GLOBAL_CONFIG.write()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to acquire config lock: {}", e)))?;
    
    // Update configuration with provided values
    if let Some(tc) = thread_count {
        if tc == 0 {
            config.thread_count = num_cpus::get();
        } else {
            config.thread_count = tc;
        }
        
        // Update Rayon thread pool (only if not already initialized)
        let mut pool_initialized = THREAD_POOL_INITIALIZED.write()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to acquire thread pool lock: {}", e)))?;
        
        if !*pool_initialized {
            rayon::ThreadPoolBuilder::new()
                .num_threads(config.thread_count)
                .build_global()
                .map_err(|e| PyRuntimeError::new_err(format!("Failed to configure thread pool: {}", e)))?;
            *pool_initialized = true;
        } else {
            // Thread pool already initialized, just update the config value
            // Note: Rayon doesn't support runtime thread pool resizing
            // The new value will be stored but won't affect the existing pool
        }
    }
    
    if let Some(cs) = chunk_size {
        if cs == 0 {
            return Err(PyValueError::new_err("chunk_size must be greater than 0"));
        }
        config.chunk_size = cs;
    }
    
    if let Some(ml) = memory_limit_mb {
        if ml == 0 {
            return Err(PyValueError::new_err("memory_limit_mb must be greater than 0"));
        }
        config.memory_limit_mb = ml;
    }
    
    if let Some(simd) = enable_simd {
        config.enable_simd = simd;
    }
    
    if let Some(cs) = cache_size {
        config.cache_size = cs;
    }
    
    Ok(())
}

/// Get current configuration settings
/// 
/// # Returns
/// Dictionary containing current configuration values
/// 
/// # Example
/// ```python
/// import insightora_core
/// config = insightora_core.get_config()
/// print(f"Thread count: {config['thread_count']}")
/// ```
#[pyfunction]
pub fn get_config() -> PyResult<PyObject> {
    let config = GLOBAL_CONFIG.read()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to acquire config lock: {}", e)))?;
    
    Python::with_gil(|py| {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("thread_count", config.thread_count)?;
        dict.set_item("chunk_size", config.chunk_size)?;
        dict.set_item("memory_limit_mb", config.memory_limit_mb)?;
        dict.set_item("enable_simd", config.enable_simd)?;
        dict.set_item("cache_size", config.cache_size)?;
        Ok(dict.into())
    })
}

/// Get the current configuration (internal use)
pub fn get_current_config() -> RustConfig {
    GLOBAL_CONFIG.read()
        .expect("Failed to read config")
        .clone()
}

/// Error types for Rust operations
#[derive(Debug, thiserror::Error)]
pub enum InsightoraError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Parse error: {0}")]
    ParseError(String),
    
    #[error("Memory limit exceeded: requested {requested}MB, limit {limit}MB")]
    MemoryLimitExceeded { requested: usize, limit: usize },
    
    #[error("Invalid data type: expected {expected}, got {actual}")]
    InvalidDataType { expected: String, actual: String },
    
    #[error("Polars error: {0}")]
    PolarsError(#[from] polars::error::PolarsError),
    
    #[error("Thread pool error: {0}")]
    ThreadPoolError(String),
    
    #[error("Configuration error: {0}")]
    ConfigError(String),
    
    #[error("Validation error: {0}")]
    ValidationError(String),
}

/// Convert Rust errors to Python exceptions
impl From<InsightoraError> for PyErr {
    fn from(err: InsightoraError) -> PyErr {
        match err {
            InsightoraError::MemoryLimitExceeded { requested, limit } => {
                PyMemoryError::new_err(format!(
                    "Memory limit exceeded: requested {}MB, limit {}MB",
                    requested, limit
                ))
            }
            InsightoraError::InvalidDataType { expected, actual } => {
                PyTypeError::new_err(format!(
                    "Invalid data type: expected {}, got {}",
                    expected, actual
                ))
            }
            InsightoraError::ValidationError(msg) => {
                PyValueError::new_err(msg)
            }
            InsightoraError::ConfigError(msg) => {
                PyValueError::new_err(format!("Configuration error: {}", msg))
            }
            InsightoraError::ParseError(msg) => {
                PyValueError::new_err(format!("Parse error: {}", msg))
            }
            InsightoraError::ThreadPoolError(msg) => {
                PyRuntimeError::new_err(format!("Thread pool error: {}", msg))
            }
            InsightoraError::IoError(e) => {
                PyRuntimeError::new_err(format!("IO error: {}", e))
            }
            InsightoraError::PolarsError(e) => {
                PyRuntimeError::new_err(format!("Polars error: {}", e))
            }
        }
    }
}

/// Helper function to validate memory usage against configured limits
pub fn check_memory_limit(estimated_mb: usize) -> Result<(), InsightoraError> {
    let config = get_current_config();
    if estimated_mb > config.memory_limit_mb {
        return Err(InsightoraError::MemoryLimitExceeded {
            requested: estimated_mb,
            limit: config.memory_limit_mb,
        });
    }
    Ok(())
}

// ============================================================================
// CSV Parsing Python Bindings
// ============================================================================

use crate::io::csv_parser::{ParallelCsvParser, CsvParserConfig, StreamingCsvParser, StreamingCsvConfig};
use pyo3::types::PyDict;

/// Parse a CSV file and return a dictionary with data
/// 
/// This function provides a simple interface for parsing CSV files from Python.
/// It uses parallel processing for improved performance on large files.
/// 
/// # Arguments
/// * `file_path` - Path to the CSV file
/// 
/// # Returns
/// * Dictionary with 'columns' (list of column names) and 'data' (list of lists)
/// 
/// # Example
/// ```python
/// import insightora_core
/// import pandas as pd
/// 
/// # Parse CSV file
/// result = insightora_core.parse_csv("data.csv")
/// 
/// # Convert to pandas DataFrame
/// df = pd.DataFrame(result['data'], columns=result['columns'])
/// ```
#[pyfunction]
pub fn parse_csv(py: Python, file_path: &str) -> PyResult<PyObject> {
    let parser = ParallelCsvParser::new();
    let df = parser.parse(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse CSV: {}", e)))?;
    
    // Convert DataFrame to dictionary format
    let result = PyDict::new(py);
    
    // Get column names
    let columns: Vec<String> = df.get_column_names()
        .iter()
        .map(|s| s.to_string())
        .collect();
    result.set_item("columns", columns)?;
    
    // Get shape
    result.set_item("num_rows", df.height())?;
    result.set_item("num_columns", df.width())?;
    
    // Convert data to nested lists (column-major format)
    let mut data_columns = Vec::new();
    for col in df.get_columns() {
        let col_data = series_to_python_list(py, col)?;
        data_columns.push(col_data);
    }
    result.set_item("data", data_columns)?;
    
    Ok(result.into())
}

/// Helper function to convert a Polars Series to a Python list
fn series_to_python_list(py: Python, series: &polars::prelude::Series) -> PyResult<PyObject> {
    use polars::prelude::*;
    use pyo3::types::PyList;
    
    let list = PyList::empty(py);
    
    // Convert series to string representation for simplicity
    // This ensures compatibility across all data types
    let string_series = series.cast(&DataType::String)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to cast series: {}", e)))?;
    
    let ca = string_series.str()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get string array: {}", e)))?;
    
    // Iterate through values
    for i in 0..ca.len() {
        let opt_val = ca.get(i);
        match opt_val {
            Some(val) => {
                // Try to parse as number if possible, otherwise keep as string
                if let Ok(num) = val.parse::<i64>() {
                    list.append(num)?;
                } else if let Ok(num) = val.parse::<f64>() {
                    list.append(num)?;
                } else if val == "true" || val == "false" {
                    list.append(val == "true")?;
                } else {
                    list.append(val)?;
                }
            }
            None => list.append(py.None())?,
        }
    }
    
    Ok(list.into())
}

/// Parse a CSV file with custom options
/// 
/// Provides fine-grained control over CSV parsing behavior.
/// 
/// # Arguments
/// * `file_path` - Path to the CSV file
/// * `has_header` - Whether the CSV has a header row (default: True)
/// * `delimiter` - Field delimiter character (default: ',')
/// * `chunk_size` - Number of rows to process per chunk (default: 100000)
/// * `infer_schema_length` - Number of rows to use for schema inference (default: 1000)
/// 
/// # Returns
/// * Dictionary with 'columns' and 'data'
/// 
/// # Example
/// ```python
/// import insightora_core
/// import pandas as pd
/// 
/// # Parse CSV with custom delimiter
/// result = insightora_core.parse_csv_with_options(
///     "data.tsv",
///     delimiter="\t",
///     chunk_size=50000
/// )
/// df = pd.DataFrame(result['data'], columns=result['columns'])
/// ```
#[pyfunction]
#[pyo3(signature = (file_path, has_header=true, delimiter=",", chunk_size=None, infer_schema_length=None))]
pub fn parse_csv_with_options(
    py: Python,
    file_path: &str,
    has_header: bool,
    delimiter: &str,
    chunk_size: Option<usize>,
    infer_schema_length: Option<usize>,
) -> PyResult<PyObject> {
    // Validate delimiter
    if delimiter.len() != 1 {
        return Err(PyValueError::new_err("Delimiter must be a single character"));
    }
    let delimiter_byte = delimiter.as_bytes()[0];
    
    // Get global config for defaults
    let global_config = get_current_config();
    
    // Build parser config
    let config = CsvParserConfig {
        chunk_size: chunk_size.unwrap_or(global_config.chunk_size),
        has_header,
        delimiter: delimiter_byte,
        quote_char: b'"',
        infer_schema_length: Some(infer_schema_length.unwrap_or(1000)),
    };
    
    let parser = ParallelCsvParser::with_config(config);
    let df = parser.parse(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse CSV: {}", e)))?;
    
    // Convert DataFrame to dictionary format
    let result = PyDict::new(py);
    
    // Get column names
    let columns: Vec<String> = df.get_column_names()
        .iter()
        .map(|s| s.to_string())
        .collect();
    result.set_item("columns", columns)?;
    
    // Get shape
    result.set_item("num_rows", df.height())?;
    result.set_item("num_columns", df.width())?;
    
    // Convert data to nested lists (column-major format)
    let mut data_columns = Vec::new();
    for col in df.get_columns() {
        let col_data = series_to_python_list(py, col)?;
        data_columns.push(col_data);
    }
    result.set_item("data", data_columns)?;
    
    Ok(result.into())
}

/// Infer schema from a CSV file without loading all data
/// 
/// This function quickly analyzes the CSV file structure and returns
/// schema information including column names and data types.
/// 
/// # Arguments
/// * `file_path` - Path to the CSV file
/// * `_sample_size` - Number of rows to sample for inference (default: 1000, currently unused)
/// 
/// # Returns
/// * Dictionary with schema information
/// 
/// # Example
/// ```python
/// import insightora_core
/// 
/// schema = insightora_core.infer_csv_schema("data.csv")
/// print(schema)
/// # {'columns': ['name', 'age', 'salary'], 'dtypes': ['String', 'Int64', 'Float64']}
/// ```
#[pyfunction]
#[pyo3(signature = (file_path, _sample_size=1000))]
pub fn infer_csv_schema(py: Python, file_path: &str, _sample_size: usize) -> PyResult<PyObject> {
    let parser = ParallelCsvParser::new();
    let schema = parser.infer_schema(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to infer schema: {}", e)))?;
    
    // Build result dictionary
    let result = PyDict::new(py);
    
    // Extract column names
    let columns: Vec<String> = schema.iter_names().map(|s| s.to_string()).collect();
    result.set_item("columns", columns)?;
    
    // Extract data types
    let dtypes: Vec<String> = schema.iter_dtypes()
        .map(|dt| format!("{:?}", dt))
        .collect();
    result.set_item("dtypes", dtypes)?;
    
    result.set_item("num_columns", schema.len())?;
    
    Ok(result.into())
}

// ============================================================================
// Streaming CSV Parser Python Bindings
// ============================================================================

/// Parse a large CSV file using streaming mode for memory efficiency
/// 
/// This function is optimized for files larger than 1GB and uses
/// memory-efficient streaming to avoid loading the entire file at once.
/// 
/// # Arguments
/// * `file_path` - Path to the CSV file
/// * `chunk_size` - Number of rows to process per chunk (default: 100000)
/// * `memory_limit_mb` - Memory limit in MB (default: 1024)
/// 
/// # Returns
/// * Dictionary with 'columns' and 'data'
/// 
/// # Example
/// ```python
/// import insightora_core
/// import pandas as pd
/// 
/// # Parse large CSV file with streaming
/// result = insightora_core.parse_csv_streaming(
///     "large_file.csv",
///     chunk_size=50000,
///     memory_limit_mb=512
/// )
/// df = pd.DataFrame(result['data'], columns=result['columns'])
/// ```
#[pyfunction]
#[pyo3(signature = (file_path, chunk_size=100000, memory_limit_mb=1024))]
pub fn parse_csv_streaming(
    py: Python,
    file_path: &str,
    chunk_size: usize,
    memory_limit_mb: usize,
) -> PyResult<PyObject> {
    let config = StreamingCsvConfig {
        chunk_size,
        memory_limit_mb,
        has_header: true,
        delimiter: b',',
    };
    
    let parser = StreamingCsvParser::with_config(config);
    let df = parser.parse_streaming(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse CSV in streaming mode: {}", e)))?;
    
    // Convert DataFrame to dictionary format
    let result = PyDict::new(py);
    
    // Get column names
    let columns: Vec<String> = df.get_column_names()
        .iter()
        .map(|s| s.to_string())
        .collect();
    result.set_item("columns", columns)?;
    
    // Get shape
    result.set_item("num_rows", df.height())?;
    result.set_item("num_columns", df.width())?;
    
    // Convert data to nested lists (column-major format)
    let mut data_columns = Vec::new();
    for col in df.get_columns() {
        let col_data = series_to_python_list(py, col)?;
        data_columns.push(col_data);
    }
    result.set_item("data", data_columns)?;
    
    Ok(result.into())
}

/// Check if streaming mode is recommended for a CSV file
/// 
/// This function analyzes the file size and estimates memory usage
/// to determine if streaming mode should be used.
/// 
/// # Arguments
/// * `file_path` - Path to the CSV file
/// * `memory_limit_mb` - Memory limit in MB (default: 1024)
/// 
/// # Returns
/// * Dictionary with recommendation and estimated memory usage
/// 
/// # Example
/// ```python
/// import insightora_core
/// 
/// info = insightora_core.should_use_streaming("large_file.csv")
/// if info['recommended']:
///     print(f"Streaming recommended. Estimated memory: {info['estimated_memory_mb']}MB")
/// ```
#[pyfunction]
#[pyo3(signature = (file_path, memory_limit_mb=1024))]
pub fn should_use_streaming(
    py: Python,
    file_path: &str,
    memory_limit_mb: usize,
) -> PyResult<PyObject> {
    let config = StreamingCsvConfig {
        memory_limit_mb,
        ..Default::default()
    };
    
    let parser = StreamingCsvParser::with_config(config);
    
    let estimated_memory = parser.estimate_memory_usage(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to estimate memory: {}", e)))?;
    
    let recommended = parser.should_use_streaming(file_path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to check streaming recommendation: {}", e)))?;
    
    let result = PyDict::new(py);
    result.set_item("recommended", recommended)?;
    result.set_item("estimated_memory_mb", estimated_memory)?;
    result.set_item("memory_limit_mb", memory_limit_mb)?;
    
    Ok(result.into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = RustConfig::default();
        assert!(config.thread_count > 0);
        assert_eq!(config.chunk_size, 100_000);
        assert_eq!(config.memory_limit_mb, 4096);
        assert!(config.enable_simd);
    }

    #[test]
    fn test_memory_limit_check() {
        let result = check_memory_limit(2048);
        assert!(result.is_ok());
        
        let result = check_memory_limit(5000);
        assert!(result.is_err());
    }
}
