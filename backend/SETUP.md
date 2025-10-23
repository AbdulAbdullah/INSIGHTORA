# Smart BI Platform - Backend Setup

## Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.8+ (check with `python --version`)
- Git

### 2. Setup
```bash
# Clone and navigate
git clone <repository-url>
cd smart-bi-platform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install essentials only
pip install fastapi uvicorn pydantic-settings sqlalchemy alembic psycopg2-binary python-dotenv

# Create uploads directory
mkdir uploads

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 3. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Environment Configuration (Optional)
Copy the `.env` file and update with your database:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bi_assistant_db
GROQ_API_KEY=your-groq-api-key
```

## That's it! 🚀

The API will start with minimal dependencies. You can add more features later by installing additional packages as needed.

## Additional Packages (Install as needed)

```bash
# For AI features
pip install langchain groq

# For data processing
pip install pandas numpy matplotlib plotly

# For background tasks
pip install celery redis

# For testing
pip install pytest httpx
```

## Troubleshooting

### Common Issues:
1. **ModuleNotFoundError**: Make sure virtual environment is activated
2. **Port already in use**: Change port with `--port 8001`
3. **Database connection**: Update DATABASE_URL in .env

### Need Help?
- Check the logs in terminal
- Visit http://localhost:8000/docs for API documentation
- Create an issue on GitHub