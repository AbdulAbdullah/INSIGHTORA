-- Smart BI Platform Database Initialization Script

-- Create database if not exists (this is handled by Docker environment)
-- CREATE DATABASE bi_assistant_db;

-- Create necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search improvements
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For improved indexing

-- Create custom types/enums (these will be handled by Alembic migrations)
-- But we can add any custom functions or initial data here

-- Function to update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create indexes for better performance (will be created by migrations)
-- These are just examples and will be handled by Alembic

-- Grant permissions to the postgres user (matches TypeScript app config)
GRANT ALL PRIVILEGES ON DATABASE bi_assistant_db TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;