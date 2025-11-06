# Smart Business Intelligence Platform

A modern, AI-powered Business Intelligence platform built with Python FastAPI backend. A comprehensive **Power BI-like** Business Intelligence platform that transforms how users interact with their data. Ask questions in natural language and get instant insights with interactive visualizations, real-time analytics, and enterprise-grade security.

## Core Features

### **Enterprise Authentication & Security**
- **Multi-Factor Authentication**: Email OTP verification for registration & login
- **Device Trust Management**: Remember trusted devices for 30 days
- **Role-Based Access Control**: Individual and Business account types
- **Security Features**: Rate limiting, account lockout, audit logging
- **Professional Email System**: Branded templates for all communications

### **Multi-Source Data Connectivity**
- **Database Support**: PostgreSQL, MySQL, SQL Server, Oracle, MongoDB
- **File Processing**: CSV, Excel, JSON uploads with automatic schema detection
- **Real-time Streaming**: Live data connections with WebSocket support
- **Cloud Integration**: AWS, Google Cloud, Azure data sources
- **API Connections**: REST APIs and webhook integrations

### **AI-Powered Analytics Engine**
- **Natural Language Queries**: "What were my top products last month?"
- **Smart SQL Generation**: AI converts conversations to optimized queries
- **Automated Insights**: Pattern detection, anomaly alerts, trend analysis
- **Predictive Analytics**: Forecasting and recommendation engine
- **Context Awareness**: Remembers conversation history and preferences

### **Advanced Visualizations**
- **20+ Chart Types**: Bar, line, pie, heatmaps, geographic maps, funnel charts
- **Interactive Dashboards**: Drag-and-drop builder with real-time updates
- **Drill-Down Capabilities**: Click to explore deeper data insights
- **Mobile Responsive**: Full functionality on all devices
- **Export Options**: PDF reports, Excel exports, scheduled delivery

### **Enterprise Features**
- **Collaboration Tools**: Share dashboards, team workspaces, comments
- **Performance Optimization**: Caching, query optimization, auto-scaling
- **Monitoring & Alerts**: Real-time system health, custom notifications
- **Compliance Ready**: GDPR, SOC2, enterprise security standards

## Project Structure

```.
├── frontend/               # React frontend
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   │   ├── core/           # Core infrastructure
│   │   ├── modules/        # Feature modules (auth, analytics, etc.)
│   │   ├── api/            # API routes and endpoints
│   │   └── shared/         # Shared utilities and constants
│   ├── requirements/       # Python dependencies
│   └── .env.example       # Environment configuration template
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## Quick Start

### Backend Setup (Python FastAPI)

```bash
# Clone the repository
git clone https://github.com/AbdulAbdullah/INSIGHTORA.git
cd INSIGHTORA/backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements/base.txt

# Setup environment
cp .env.example .env
# Edit .env with your database and API credentials

# Run the application
uvicorn app.main:app --reload
```

**API Documentation**: http://localhost:8000/docs

## Technology Stack

### **Backend Infrastructure**
- **Framework**: Python FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with multi-factor authentication
- **Caching**: Redis for high-performance data caching
- **AI Engine**: Configurable AI providers (Groq, OpenAI)
- **Email Service**: SMTP with professional templates
- **Security**: Comprehensive security middleware and validation

### **Key Features**
- 🤖 **AI-Powered Analytics**: Natural language to SQL conversion
- 📊 **Interactive Visualizations**: Multiple chart types and dashboards
- 🔗 **Multi-Database Support**: PostgreSQL, MySQL, SQL Server, Oracle
- 📁 **File Processing**: CSV, Excel, JSON, Parquet support
- 🔐 **Enterprise Security**: JWT authentication, encryption, audit logging
- ⚡ **High Performance**: Async FastAPI, Redis caching, optimized queries

## Configuration

### Environment Setup

Create a `.env` file in the backend directory using `.env.example` as a template:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_database_name

# Security Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
REFRESH_SECRET_KEY=your-refresh-secret-key-change-this-in-production

# AI Configuration (Optional)
AI_API_KEY=your_ai_api_key_here
AI_MODEL=your-preferred-model

# Email Configuration (Optional)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_email_password
```

## Development

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Development Setup
```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Features

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/verify` - OTP verification
- `POST /api/v1/auth/refresh` - Token refresh

### Data Analytics
- `POST /api/v1/analytics/query` - Natural language queries
- `GET /api/v1/analytics/history` - Query history
- `POST /api/v1/data/upload` - File upload and processing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Support

If you encounter any issues:
1. Check the API documentation at `/docs`
2. Review the environment configuration
3. Check the application logs
4. Open an issue on GitHub

---

**Built with FastAPI | Designed for Enterprise**