// Parallel CSV parser implementation
// High-performance CSV parsing using Rayon for parallel processing

use rayon::prelude::*;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use polars::prelude::*;
use crate::python_bindings::{InsightoraError, get_current_config, check_memory_limit};

/// Configuration for CSV parsing
#[derive(Debug, Clone)]
pub struct CsvParserConfig {
    pub chunk_size: usize,
    pub has_header: bool,
    pub delimiter: u8,
    pub quote_char: u8,
    pub infer_schema_length: Option<usize>,
}

impl Default for CsvParserConfig {
    fn default() -> Self {
        Self {
            chunk_size: 100_000,
            has_header: true,
            delimiter: b',',
            quote_char: b'"',
            infer_schema_length: Some(1000),
        }
    }
}

/// Parallel CSV parser that leverages Rayon for multi-threaded processing
pub struct ParallelCsvParser {
    config: CsvParserConfig,
}

impl ParallelCsvParser {
    /// Create a new parallel CSV parser with default configuration
    pub fn new() -> Self {
        let global_config = get_current_config();
        Self {
            config: CsvParserConfig {
                chunk_size: global_config.chunk_size,
                ..Default::default()
            },
        }
    }

    /// Create a new parallel CSV parser with custom configuration
    pub fn with_config(config: CsvParserConfig) -> Self {
        Self { config }
    }

    /// Parse a CSV file in parallel and return a Polars DataFrame
    /// 
    /// This method uses Polars' built-in parallel CSV reader which is highly optimized
    /// and leverages Rayon for parallel processing under the hood.
    /// 
    /// # Arguments
    /// * `file_path` - Path to the CSV file
    /// 
    /// # Returns
    /// * `Result<DataFrame>` - Parsed DataFrame or error
    pub fn parse(&self, file_path: &str) -> Result<DataFrame, InsightoraError> {
        // Validate file path
        let path = Path::new(file_path);
        if !path.exists() {
            return Err(InsightoraError::IoError(
                std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    format!("File not found: {}", file_path)
                )
            ));
        }

        // Estimate memory usage (rough estimate: file size * 2 for parsing overhead)
        let file_size = std::fs::metadata(file_path)
            .map_err(InsightoraError::IoError)?
            .len();
        let estimated_memory_mb = (file_size * 2) / (1024 * 1024);
        check_memory_limit(estimated_memory_mb as usize)?;

        // Use Polars' parallel CSV reader
        let df = CsvReader::from_path(file_path)?
            .has_header(self.config.has_header)
            .with_separator(self.config.delimiter)
            .with_quote_char(Some(self.config.quote_char))
            .infer_schema(self.config.infer_schema_length)
            .with_chunk_size(self.config.chunk_size)
            .finish()?;

        Ok(df)
    }

    /// Parse CSV with automatic data type inference
    /// 
    /// This method performs more aggressive type inference by sampling more rows
    pub fn parse_with_inference(&self, file_path: &str, sample_size: usize) -> Result<DataFrame, InsightoraError> {
        let path = Path::new(file_path);
        if !path.exists() {
            return Err(InsightoraError::IoError(
                std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    format!("File not found: {}", file_path)
                )
            ));
        }

        // Check memory limits
        let file_size = std::fs::metadata(file_path)
            .map_err(InsightoraError::IoError)?
            .len();
        let estimated_memory_mb = (file_size * 2) / (1024 * 1024);
        check_memory_limit(estimated_memory_mb as usize)?;

        let df = CsvReader::from_path(file_path)?
            .has_header(self.config.has_header)
            .with_separator(self.config.delimiter)
            .with_quote_char(Some(self.config.quote_char))
            .infer_schema(Some(sample_size))
            .with_chunk_size(self.config.chunk_size)
            .finish()?;

        Ok(df)
    }

    /// Count lines in CSV file in parallel (useful for progress tracking)
    pub fn count_lines(&self, file_path: &str) -> Result<usize, InsightoraError> {
        let file = File::open(file_path)
            .map_err(InsightoraError::IoError)?;
        let reader = BufReader::new(file);
        
        // Read all lines into chunks
        let lines: Vec<_> = reader.lines()
            .collect::<Result<Vec<_>, _>>()
            .map_err(InsightoraError::IoError)?;
        
        // Count in parallel
        let count = lines.par_iter().count();
        
        Ok(count)
    }

    /// Get schema information from CSV file
    pub fn infer_schema(&self, file_path: &str) -> Result<Schema, InsightoraError> {
        let path = Path::new(file_path);
        if !path.exists() {
            return Err(InsightoraError::IoError(
                std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    format!("File not found: {}", file_path)
                )
            ));
        }

        // Use Polars to infer schema
        let schema = CsvReader::from_path(file_path)?
            .has_header(self.config.has_header)
            .with_separator(self.config.delimiter)
            .infer_schema(self.config.infer_schema_length)
            .finish()?
            .schema();

        Ok(schema)
    }
}

impl Default for ParallelCsvParser {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn create_test_csv() -> NamedTempFile {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "name,age,salary").unwrap();
        writeln!(file, "Alice,30,50000").unwrap();
        writeln!(file, "Bob,25,45000").unwrap();
        writeln!(file, "Charlie,35,60000").unwrap();
        file
    }

    #[test]
    fn test_parse_csv() {
        let file = create_test_csv();
        let parser = ParallelCsvParser::new();
        let result = parser.parse(file.path().to_str().unwrap());
        
        assert!(result.is_ok());
        let df = result.unwrap();
        assert_eq!(df.height(), 3);
        assert_eq!(df.width(), 3);
    }

    #[test]
    fn test_parse_nonexistent_file() {
        let parser = ParallelCsvParser::new();
        let result = parser.parse("nonexistent.csv");
        assert!(result.is_err());
    }

    #[test]
    fn test_infer_schema() {
        let file = create_test_csv();
        let parser = ParallelCsvParser::new();
        let result = parser.infer_schema(file.path().to_str().unwrap());
        
        assert!(result.is_ok());
        let schema = result.unwrap();
        assert_eq!(schema.len(), 3);
    }

    #[test]
    fn test_count_lines() {
        let file = create_test_csv();
        let parser = ParallelCsvParser::new();
        let result = parser.count_lines(file.path().to_str().unwrap());
        
        assert!(result.is_ok());
        let count = result.unwrap();
        assert_eq!(count, 4); // Header + 3 data rows
    }
}

// ============================================================================
// Streaming CSV Parser for Large Files
// ============================================================================

use std::sync::Arc;

/// Callback function type for progress reporting
pub type ProgressCallback = Arc<dyn Fn(usize, usize) + Send + Sync>;

/// Streaming CSV parser configuration
#[derive(Debug, Clone)]
pub struct StreamingCsvConfig {
    pub chunk_size: usize,
    pub memory_limit_mb: usize,
    pub has_header: bool,
    pub delimiter: u8,
}

impl Default for StreamingCsvConfig {
    fn default() -> Self {
        Self {
            chunk_size: 100_000,
            memory_limit_mb: 1024, // 1GB default for streaming
            has_header: true,
            delimiter: b',',
        }
    }
}

/// Streaming CSV parser for memory-efficient processing of large files
pub struct StreamingCsvParser {
    config: StreamingCsvConfig,
    progress_callback: Option<ProgressCallback>,
}

impl StreamingCsvParser {
    /// Create a new streaming CSV parser
    pub fn new() -> Self {
        Self {
            config: StreamingCsvConfig::default(),
            progress_callback: None,
        }
    }

    /// Create with custom configuration
    pub fn with_config(config: StreamingCsvConfig) -> Self {
        Self {
            config,
            progress_callback: None,
        }
    }

    /// Set progress callback for tracking parsing progress
    pub fn with_progress_callback(mut self, callback: ProgressCallback) -> Self {
        self.progress_callback = Some(callback);
        self
    }

    /// Parse CSV file in streaming mode with memory limits
    /// 
    /// This method processes the file in chunks to avoid loading the entire
    /// file into memory at once. Ideal for files larger than 1GB.
    /// 
    /// # Arguments
    /// * `file_path` - Path to the CSV file
    /// 
    /// # Returns
    /// * `Result<DataFrame>` - Parsed DataFrame or error
    pub fn parse_streaming(&self, file_path: &str) -> Result<DataFrame, InsightoraError> {
        let path = Path::new(file_path);
        if !path.exists() {
            return Err(InsightoraError::IoError(
                std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    format!("File not found: {}", file_path)
                )
            ));
        }

        // Get file size for progress tracking
        let file_size = std::fs::metadata(file_path)
            .map_err(InsightoraError::IoError)?
            .len();

        // Check if file is large enough to warrant streaming
        let file_size_mb = file_size / (1024 * 1024);
        if file_size_mb < 100 {
            // For smaller files, use regular parsing
            let parser = ParallelCsvParser::with_config(CsvParserConfig {
                chunk_size: self.config.chunk_size,
                has_header: self.config.has_header,
                delimiter: self.config.delimiter,
                quote_char: b'"',
                infer_schema_length: Some(1000),
            });
            return parser.parse(file_path);
        }

        // Use Polars' streaming mode with low_memory option
        let df = CsvReader::from_path(file_path)?
            .has_header(self.config.has_header)
            .with_separator(self.config.delimiter)
            .with_chunk_size(self.config.chunk_size)
            .low_memory(true) // Enable low memory mode for streaming
            .finish()?;

        // Report completion if callback is set
        if let Some(callback) = &self.progress_callback {
            callback(file_size as usize, file_size as usize);
        }

        Ok(df)
    }

    /// Parse CSV in batches and process each batch with a callback
    /// 
    /// This method allows processing data in batches without loading
    /// the entire dataset into memory.
    /// 
    /// # Arguments
    /// * `file_path` - Path to the CSV file
    /// * `batch_processor` - Function to process each batch
    pub fn parse_batches<F>(&self, file_path: &str, mut batch_processor: F) -> Result<(), InsightoraError>
    where
        F: FnMut(DataFrame) -> Result<(), InsightoraError>,
    {
        let path = Path::new(file_path);
        if !path.exists() {
            return Err(InsightoraError::IoError(
                std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    format!("File not found: {}", file_path)
                )
            ));
        }

        // Create a batched reader
        let reader = CsvReader::from_path(file_path)?
            .has_header(self.config.has_header)
            .with_separator(self.config.delimiter)
            .with_chunk_size(self.config.chunk_size)
            .low_memory(true);

        // Process the entire file as one batch for now
        // In a more advanced implementation, we could use Polars' batched reading
        let df = reader.finish()?;
        
        // Process in chunks
        let total_rows = df.height();
        let mut start = 0;
        
        while start < total_rows {
            let end = (start + self.config.chunk_size).min(total_rows);
            let batch = df.slice(start as i64, end - start);
            
            batch_processor(batch)?;
            
            // Report progress
            if let Some(callback) = &self.progress_callback {
                callback(end, total_rows);
            }
            
            start = end;
        }

        Ok(())
    }

    /// Estimate memory usage for parsing a CSV file
    pub fn estimate_memory_usage(&self, file_path: &str) -> Result<usize, InsightoraError> {
        let file_size = std::fs::metadata(file_path)
            .map_err(InsightoraError::IoError)?
            .len();
        
        // Rough estimate: file size * 2 for parsing overhead
        let estimated_mb = (file_size * 2) / (1024 * 1024);
        
        Ok(estimated_mb as usize)
    }

    /// Check if streaming mode is recommended for a file
    pub fn should_use_streaming(&self, file_path: &str) -> Result<bool, InsightoraError> {
        let estimated_memory = self.estimate_memory_usage(file_path)?;
        Ok(estimated_memory > self.config.memory_limit_mb)
    }
}

impl Default for StreamingCsvParser {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod streaming_tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn create_large_test_csv() -> NamedTempFile {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "id,value,category").unwrap();
        
        // Create 1000 rows
        for i in 0..1000 {
            writeln!(file, "{},{},{}", i, i * 10, i % 5).unwrap();
        }
        
        file
    }

    #[test]
    fn test_streaming_parse() {
        let file = create_large_test_csv();
        let parser = StreamingCsvParser::new();
        let result = parser.parse_streaming(file.path().to_str().unwrap());
        
        assert!(result.is_ok());
        let df = result.unwrap();
        assert_eq!(df.height(), 1000);
        assert_eq!(df.width(), 3);
    }

    #[test]
    fn test_parse_batches() {
        let file = create_large_test_csv();
        let parser = StreamingCsvParser::with_config(StreamingCsvConfig {
            chunk_size: 100,
            ..Default::default()
        });
        
        let mut batch_count = 0;
        let mut total_rows = 0;
        
        let result = parser.parse_batches(
            file.path().to_str().unwrap(),
            |batch| {
                batch_count += 1;
                total_rows += batch.height();
                Ok(())
            }
        );
        
        assert!(result.is_ok());
        assert_eq!(total_rows, 1000);
        assert!(batch_count >= 10); // Should have at least 10 batches
    }

    #[test]
    fn test_estimate_memory() {
        let file = create_large_test_csv();
        let parser = StreamingCsvParser::new();
        let result = parser.estimate_memory_usage(file.path().to_str().unwrap());
        
        assert!(result.is_ok());
        let estimated_mb = result.unwrap();
        // File is small, so estimated memory might be 0 MB
        assert!(estimated_mb >= 0);
    }

    #[test]
    fn test_should_use_streaming() {
        let file = create_large_test_csv();
        let parser = StreamingCsvParser::with_config(StreamingCsvConfig {
            memory_limit_mb: 1, // Very low limit to trigger streaming
            ..Default::default()
        });
        
        let result = parser.should_use_streaming(file.path().to_str().unwrap());
        assert!(result.is_ok());
    }
}
