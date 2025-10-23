# Smart BI Platform - Backend

A modern FastAPI backend for business intelligence and data analytics.

## 🚀 Quick Start

```bash
# 1. Run automated setup
./simple_setup.sh

# 2. Start the server  
./start_simple.sh

# 3. Visit the API docs
open http://localhost:8000/docs
```

That's it! You now have a running FastAPI server with interactive documentation.

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── data_sources.py    # Data source management
│   │   ├── queries.py         # Query processing
│   │   ├── dashboards.py      # Dashboard management
│   │   └── __init__.py        # API router configuration
│   ├── core/                  # Core application logic
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── security.py        # Security utilities
│   │   ├── middleware.py      # Custom middleware
│   │   └── celery.py          # Background task configuration
│   ├── models/                # SQLAlchemy database models
│   │   ├── user.py           # User model and authentication
│   │   ├── data_source.py    # Data source connections
│   │   ├── query_history.py  # Query tracking and history
│   │   └── dashboard.py      # Dashboard and widget models
│   ├── utils/                 # Utility functions
│   │   ├── exceptions.py     # Custom exception classes
│   │   ├── data_processor.py # Data processing utilities
│   │   └── validators.py     # Pydantic validators
│   └── main.py               # FastAPI application entry point
├── alembic/                   # Database migrations
├── uploads/                   # File upload storage
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service orchestration
└── setup.sh                # Development setup script
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (recommended)

### Quick Start with Docker (Recommended)

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Database Admin: http://localhost:5050 (pgAdmin)
   - Task Monitor: http://localhost:5555 (Flower)

### Manual Development Setup

1. **Run setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up database**
   ```bash
   # Start PostgreSQL and Redis
   # Create database
   createdb smart_bi_db
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start the application**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Start FastAPI
   uvicorn app.main:app --reload
   
   # In separate terminals:
   celery -A app.core.celery worker --loglevel=info
   celery -A app.core.celery beat --loglevel=info
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smart_bi_db

# Security
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=true
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Redis
REDIS_URL=redis://localhost:6379/0

# File Uploads
MAX_FILE_SIZE_MB=100
UPLOAD_DIRECTORY=./uploads

# AI/ML APIs
GROQ_API_KEY=your-groq-api-key
LANGCHAIN_API_KEY=your-langchain-api-key
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user info

### Data Source Management
- `POST /api/v1/data-sources` - Create data source
- `GET /api/v1/data-sources` - List data sources
- `POST /api/v1/data-sources/upload` - Upload files
- `GET /api/v1/data-sources/{id}/preview` - Preview data

### Query Processing
- `POST /api/v1/queries` - Create natural language query
- `GET /api/v1/queries` - Query history
- `POST /api/v1/queries/execute` - Execute query
- `POST /api/v1/queries/{id}/favorite` - Mark as favorite

### Dashboard Management
- `POST /api/v1/dashboards` - Create dashboard
- `GET /api/v1/dashboards` - List dashboards
- `POST /api/v1/dashboards/{id}/widgets` - Add widget
- `PUT /api/v1/dashboards/{id}/widgets/{widget_id}` - Update widget

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password encryption
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: API rate limiting and throttling
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries

## 📊 Data Processing Pipeline

1. **Data Ingestion**: Support for CSV, Excel, JSON, database connections
2. **Data Validation**: Schema validation and type checking
3. **Data Transformation**: pandas-based data cleaning and processing
4. **AI Query Processing**: Natural language to SQL translation
5. **Result Visualization**: Automatic chart generation
6. **Caching Layer**: Redis-based result caching

## 🤖 AI Integration

### Natural Language Processing
- **LangChain Framework**: For building AI-powered applications
- **Groq LLaMA Models**: High-performance language models
- **spaCy NLP**: Advanced text processing and entity recognition
- **Query Understanding**: Context-aware SQL generation

### Machine Learning Features
- **Auto-visualization**: Intelligent chart type selection
- **Pattern Detection**: Anomaly detection in data
- **Predictive Analytics**: Time series forecasting
- **Smart Recommendations**: Query and visualization suggestions

## 🔄 Background Tasks

### Celery Integration
- **Data Processing Jobs**: Long-running data operations
- **Scheduled Reports**: Automated report generation
- **Cache Warming**: Precompute frequently accessed data
- **Email Notifications**: Async notification system

### Task Monitoring
- **Flower Dashboard**: Real-time task monitoring
- **Health Checks**: System health and performance monitoring
- **Error Tracking**: Comprehensive error logging

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test module
pytest tests/test_auth.py

# Run integration tests
pytest tests/integration/
```

## 📈 Performance Optimization

### Database Optimization
- **Connection Pooling**: SQLAlchemy connection pool management
- **Query Optimization**: Efficient queries with proper indexing
- **Pagination**: Large dataset handling
- **Caching Strategy**: Multi-level caching with Redis

### API Performance
- **Async Operations**: FastAPI async request handling
- **Background Tasks**: Offload heavy processing to Celery
- **Response Compression**: Gzip compression for large responses
- **Database Indexing**: Optimized database indexes

## 🐳 Docker Support

### Development Environment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Build production image
docker build -t smart-bi-backend:latest .

# Run with production config
docker run -d \
  --name smart-bi-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  smart-bi-backend:latest
```

## 📋 Monitoring & Logging

### Application Monitoring
- **Health Checks**: Comprehensive system health endpoints
- **Metrics Collection**: Performance and usage metrics
- **Error Tracking**: Detailed error logging and reporting
- **Performance Monitoring**: Request/response time tracking

### Database Monitoring
- **Connection Monitoring**: Database connection health
- **Query Performance**: Slow query identification
- **Resource Usage**: Memory and CPU monitoring

## 🚀 Deployment

### Production Checklist
- [ ] Update environment variables for production
- [ ] Configure database with proper security
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategies
- [ ] Update CORS and security settings

### Environment-Specific Configurations
- **Development**: Debug mode, detailed logging
- **Staging**: Production-like with test data
- **Production**: Optimized performance, security hardened

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: GitHub Issues
- **Discord**: Community Support Channel
- **Email**: support@smartbi.com

---

Built with ❤️ by the Smart BI Platform Team