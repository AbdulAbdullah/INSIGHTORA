// INSIGHTORA Core - Rust Performance Optimization Module
// High-performance data processing operations for Python integration

use pyo3::prelude::*;

// Module declarations
pub mod io;
pub mod dataframe;
pub mod stats;
pub mod streaming;
pub mod query;
pub mod utils;

// Python bindings module
pub mod python_bindings;

// Re-export commonly used types
pub use python_bindings::{InsightoraError, RustConfig};

/// PyO3 module initialization
/// This function is called when the module is imported in Python
#[pymodule]
fn insightora_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Module metadata
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "INSIGHTORA Team")?;
    
    // Configuration functions
    m.add_function(wrap_pyfunction!(python_bindings::configure, m)?)?;
    m.add_function(wrap_pyfunction!(python_bindings::get_config, m)?)?;
    
    // CSV parsing functions
    m.add_function(wrap_pyfunction!(python_bindings::parse_csv, m)?)?;
    m.add_function(wrap_pyfunction!(python_bindings::parse_csv_with_options, m)?)?;
    m.add_function(wrap_pyfunction!(python_bindings::infer_csv_schema, m)?)?;
    
    // Streaming CSV parsing functions
    m.add_function(wrap_pyfunction!(python_bindings::parse_csv_streaming, m)?)?;
    m.add_function(wrap_pyfunction!(python_bindings::should_use_streaming, m)?)?;
    
    Ok(())
}
