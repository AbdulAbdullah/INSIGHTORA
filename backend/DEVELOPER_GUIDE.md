# Smart BI Platform - Developer Guide

## 🚀 Quick Start (Recommended for New Developers)

### 1. Simple Setup
```bash
# Clone and navigate to backend
cd backend

# Run automated setup
./simple_setup.sh

# Start simple server (minimal dependencies)
./start_simple.sh
```

Visit http://localhost:8000/docs to see the API documentation!

## 📋 What Gets Installed

### Essential Packages (Minimal Setup)
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic Settings** - Configuration management  
- **SQLAlchemy** - Database ORM
- **PostgreSQL drivers** (psycopg2-binary, asyncpg)
- **Authentication** (python-jose, passlib)
- **File uploads** (python-multipart)

### Advanced Packages (Optional)
- **AI/ML**: langchain, groq, openai
- **Data Processing**: pandas, numpy, matplotlib, plotly
- **Background Tasks**: celery, redis
- **Caching**: redis

## 🛠️ Setup Options

### Option 1: Simple Mode (Recommended First)
```bash
./start_simple.sh
```
- ✅ Minimal dependencies
- ✅ Fast startup
- ✅ Core API functionality
- ✅ Interactive documentation
- ✅ Health checks

### Option 2: Full Mode (Complete Features)
```bash
./start.sh
```
- ✅ All features enabled
- ✅ Database connections
- ✅ Authentication system
- ✅ Data processing
- ⚠️ Requires PostgreSQL setup

## 🗄️ Database Setup (For Full Mode)

### PostgreSQL Configuration
1. Install PostgreSQL
2. Create database: `bi_assistant_db`
3. Update `.env` file:
```env
DATABASE_URL=postgresql://username:password@localhost/bi_assistant_db
SECRET_KEY=your-secret-key-here-32-chars-minimum
```

### Database Migration
```bash
# Activate virtual environment
source venv/Scripts/activate  # Windows
source venv/bin/activate       # Linux/Mac

# Run migrations
alembic upgrade head
```

## 📁 Project Structure

```
backend/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── models/            # Database models
│   └── utils/             # Utilities
├── venv/                  # Virtual environment
├── uploads/               # File uploads
├── requirements_essential.txt  # Minimal dependencies
├── requirements.txt       # Full dependencies
├── simple_setup.sh        # Automated setup
├── start_simple.sh        # Simple server start
└── start.sh              # Full server start
```

## 🌐 Available Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/status` - API status

### Full Mode Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/data-sources` - List data sources
- `POST /api/queries` - Execute queries
- `GET /api/dashboards` - List dashboards

## 🔧 Development Workflow

### 1. Start Development
```bash
# First time setup
./simple_setup.sh

# Start in simple mode for basic development
./start_simple.sh
```

### 2. Test Your Changes
- Visit http://localhost:8000/docs
- Use the interactive API documentation
- Test endpoints directly in browser

### 3. Add Advanced Features
```bash
# Install additional packages as needed
pip install pandas numpy matplotlib
pip install langchain openai

# Switch to full mode
./start.sh
```

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Solution: Install missing packages
pip install package-name
```

**2. Database Connection Errors**
```bash
# Solution: Check PostgreSQL is running
# Update .env with correct credentials
```

**3. Permission Denied (Windows)**
```bash
# Solution: Run in Git Bash or WSL
# Or use batch files: start.bat
```

**4. Port Already in Use**
```bash
# Solution: Stop existing server or use different port
uvicorn main_simple:app --port 8001
```

### Getting Help

1. **Check logs** - Terminal output shows detailed errors
2. **Validate setup** - Run `./simple_setup.sh` again
3. **Test minimal** - Use `./start_simple.sh` first
4. **Check dependencies** - Ensure all packages installed

## 🎯 Next Steps

### Phase 1: Core Setup ✅
- [x] FastAPI backend structure
- [x] Essential dependencies
- [x] Developer-friendly setup
- [x] Interactive documentation

### Phase 2: Authentication & Data
- [ ] User authentication system
- [ ] Database connection
- [ ] Data source management
- [ ] Query execution

### Phase 3: AI Analytics
- [ ] AI query generation
- [ ] Data visualization
- [ ] Dashboard creation
- [ ] Advanced analytics

## 💡 Tips for Success

1. **Start simple** - Use simple mode first
2. **Test frequently** - Check http://localhost:8000/docs
3. **Read logs** - Terminal output is very helpful
4. **Use virtual environment** - Keeps dependencies clean
5. **Update gradually** - Add features incrementally

---

**Ready to build something amazing!** 🚀

The Smart BI Platform is designed to be developer-friendly from day one. Start with the simple setup, explore the API docs, and gradually add the features you need.