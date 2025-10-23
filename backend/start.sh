#!/bin/bash

# Smart BI Platform - Start Server
# Simple script to start the FastAPI development server

echo "🚀 Starting Smart BI Platform API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run: ./simple_setup.sh first"
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Check if FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not installed!"
    echo "💡 Run: pip install -r requirements_essential.txt"
    exit 1
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo "🎯 Starting FastAPI server..."
echo "📚 Visit http://localhost:8000/docs for API documentation"
echo "🔍 Visit http://localhost:8000/health for health check"
echo ""
echo "🛑 Press Ctrl+C to stop"
echo "========================================"

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000