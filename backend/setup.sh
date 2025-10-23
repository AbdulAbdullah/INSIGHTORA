#!/bin/bash

# Smart BI Platform - Development Setup Script

set -e

echo "🚀 Setting up Smart BI Platform Development Environment..."

# Check if Python is installed (Windows compatibility)
PYTHON_CMD=""
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 is required but not installed."
    echo "💡 Install Python from https://python.org or Microsoft Store"
    exit 1
fi

echo "✅ Found Python: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    echo "❌ Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment (Windows compatibility)
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://smart_bi_user:smart_bi_password@localhost:5432/smart_bi_db

# Security Settings
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=true
ALLOWED_HOSTS=["localhost", "127.0.0.1", "0.0.0.0"]

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0

# File Upload Settings
MAX_FILE_SIZE_MB=100
UPLOAD_DIRECTORY=./uploads

# AI/ML Configuration
GROQ_API_KEY=your-groq-api-key-here
LANGCHAIN_API_KEY=your-langchain-api-key-here
EOF
    echo "✅ Created .env file. Please update with your actual configuration values."
fi

# Create uploads directory
mkdir -p uploads
echo "📁 Created uploads directory"

# Set up pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🐳 To start with Docker (recommended):"
echo "   docker-compose up -d"
echo ""
echo "💻 To start manually:"
echo "   1. Start PostgreSQL and Redis services"
echo "   2. Run database migrations: alembic upgrade head"
echo "   3. Start the application: uvicorn app.main:app --reload"
echo ""
echo "📖 API Documentation will be available at:"
echo "   - http://localhost:8000/docs (Swagger UI)"
echo "   - http://localhost:8000/redoc (ReDoc)"
echo ""
echo "🎯 Next steps:"
echo "   1. Update .env file with your database and API keys"
echo "   2. Set up PostgreSQL database"
echo "   3. Run initial migrations"
echo "   4. Start the development server"