#!/bin/bash

# Smart BI Platform - Simple Setup Script
# Works on Windows (Git Bash), Linux, and Mac

echo "🚀 Smart BI Platform - Quick Setup"
echo "=================================="

# Find Python executable
PYTHON=""
if command -v python &> /dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON="python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    echo "❌ Python 3.8+ required. Install from https://python.org"
    exit 1
fi

echo "✅ Found Python: $($PYTHON --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
$PYTHON -m pip install --upgrade pip

# Install minimal requirements
echo "📚 Installing essential packages..."
pip install fastapi uvicorn pydantic-settings sqlalchemy alembic psycopg2-binary python-dotenv

# Create directories
echo "📁 Creating directories..."
mkdir -p uploads

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bi_assistant_db

# Security Settings
SECRET_KEY=your_super_secure_jwt_secret_here_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=development
DEBUG=true

# Groq API (optional)
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.1-8b-instant
EOF
    echo "✅ Created .env file - update with your configuration"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 Start the server:"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "📚 Then visit:"
echo "   http://localhost:8000/docs (API Documentation)"
echo "   http://localhost:8000/health (Health Check)"
echo ""
echo "💡 Pro tip: Keep this terminal open and run the uvicorn command above"