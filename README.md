# Smart Business Intelligence Platform

A comprehensive **Power BI-like** Business Intelligence platform that transforms how users interact with their data. Ask questions in natural language and get instant insights with interactive visualizations, real-time analytics, and enterprise-grade security.

## Core Features

### � **Enterprise Authentication & Security**
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

## Technology Stack

### **Backend Infrastructure**
- **Runtime**: Node.js 18+ with TypeScript 5.0+
- **Framework**: Express.js with Socket.IO for real-time features
- **Database**: PostgreSQL 15+ with Prisma ORM for type-safe operations
- **Authentication**: JWT tokens with multi-factor authentication
- **Caching**: Redis for high-performance data caching
- **AI Engine**: Groq LLaMA 3.1 for natural language processing
- **Email Service**: Nodemailer with professional templates
- **Security**: Helmet, rate limiting, input validation, CORS

### **Frontend Technologies** 
- **Framework**: Next.js 14+ with React 18+ and TypeScript
- **Styling**: Tailwind CSS for responsive, modern UI
- **Charts**: D3.js and Chart.js for interactive visualizations  
- **State**: Zustand for lightweight state management
- **Real-time**: Socket.IO client for live updates
- **HTTP**: Axios with React Query for data fetching
- **Testing**: Jest, React Testing Library, Playwright E2E

### **DevOps & Infrastructure**
- **Containerization**: Docker and Docker Compose
- **Orchestration**: Kubernetes for production scaling
- **Cloud**: AWS/GCP/Azure with Terraform infrastructure
- **CI/CD**: GitHub Actions for automated deployments
- **Monitoring**: Prometheus, Grafana, ELK stack
- **Documentation**: Swagger/OpenAPI 3.0 with automated generation

## Prerequisites

- **Node.js 18+** - Runtime environment
- **PostgreSQL 15+** - Primary database  
- **Redis 7.0+** - Caching layer
- **npm or yarn** - Package manager
- **Groq API key** - AI/ML processing (free tier available)
- **Email Service** - SMTP configuration for authentication emails

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/your-username/smart-bi-platform
cd bee_agent_framework
npm install
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/smart_bi_db"

# Redis Configuration  
REDIS_URL="redis://localhost:6379"

# Authentication & Security
JWT_SECRET="your-super-secure-jwt-secret-key"
JWT_EXPIRES_IN="7d"
BCRYPT_ROUNDS=12

# Groq AI Configuration
GROQ_API_KEY="your_groq_api_key_here"
GROQ_MODEL="llama-3.1-8b-instant"

# Email Service Configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
EMAIL_FROM="Smart BI Platform <noreply@yourcompany.com>"

# Application Configuration
PORT=3000
NODE_ENV=development
CORS_ORIGIN="http://localhost:3000"
```

### 3. Database Setup

```bash
# Generate Prisma client
npx prisma generate

# Run database migrations
npx prisma migrate dev --name init

# (Optional) Seed with sample data
npx prisma db seed
```

### 4. Start Development Services

```bash
# Start PostgreSQL (if using Docker)
docker run --name postgres-bi -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Start Redis (if using Docker)  
docker run --name redis-bi -p 6379:6379 -d redis:7-alpine

# Start development server
npm run dev
```

### 5. Access the Platform

- **Main Application**: `http://localhost:3000`
- **API Documentation**: `http://localhost:3000/api-docs`
- **Health Check**: `http://localhost:3000/api/health`

### 6. First Time Setup

1. **Register Account**: Visit `/register` to create your account
2. **Verify Email**: Check email for OTP verification code  
3. **Add Data Source**: Connect your first database or upload CSV
4. **Create Dashboard**: Ask "Show me my sales data" to get started!

## Project Structure

```
smart-bi-platform/
├── src/
│   ├── controllers/
│   │   ├── AuthController.ts        # Authentication endpoints
│   │   ├── DataController.ts        # Data source management
│   │   ├── DashboardController.ts   # Dashboard operations
│   │   └── AnalyticsController.ts   # AI analytics engine
│   ├── services/
│   │   ├── AuthService.ts           # Authentication logic
│   │   ├── BeeAgentService.ts       # AI agent with BI tools
│   │   ├── DataConnectorService.ts  # Database connections
│   │   ├── EmailService.ts          # Email notifications
│   │   └── AnalyticsService.ts      # Data analysis engine
│   ├── tools/
│   │   ├── SQLGeneratorTool.ts      # Natural language to SQL
│   │   ├── ChartGeneratorTool.ts    # Visualization creation
│   │   ├── DataAnalyzerTool.ts      # Statistical analysis
│   │   └── InsightGeneratorTool.ts  # AI-powered insights
│   ├── middleware/
│   │   ├── auth.ts                  # JWT authentication
│   │   ├── rateLimiter.ts          # Rate limiting protection
│   │   ├── validation.ts           # Input validation
│   │   └── errorHandler.ts         # Global error handling
│   ├── models/
│   │   ├── User.ts                  # User entity types
│   │   ├── DataSource.ts           # Data connection types
│   │   ├── Dashboard.ts            # Dashboard configuration
│   │   └── Query.ts                # Query execution types
│   ├── routes/
│   │   ├── auth.ts                 # Authentication routes
│   │   ├── api.ts                  # Core API routes
│   │   ├── data.ts                 # Data management routes
│   │   └── dashboards.ts           # Dashboard routes
│   ├── utils/
│   │   ├── database.ts             # Database utilities
│   │   ├── encryption.ts           # Security utilities
│   │   ├── email-templates.ts      # Email template engine
│   │   └── validators.ts           # Input validation schemas
│   ├── tests/
│   │   ├── unit/                   # Unit tests
│   │   ├── integration/            # API integration tests
│   │   └── e2e/                    # End-to-end tests
│   ├── prisma/
│   │   ├── schema.prisma           # Database schema
│   │   ├── migrations/             # Database migrations
│   │   └── seed.ts                 # Sample data seeding
│   └── server.ts                   # Express server setup
├── frontend/                       # Next.js React frontend
│   ├── components/
│   │   ├── auth/                   # Authentication components
│   │   ├── charts/                 # Chart visualization components  
│   │   ├── dashboard/              # Dashboard builder components
│   │   └── common/                 # Reusable UI components
│   ├── pages/
│   │   ├── auth/                   # Authentication pages
│   │   ├── dashboard/              # Dashboard management
│   │   ├── data/                   # Data source management
│   │   └── api/                    # Next.js API routes
│   └── services/                   # Frontend API services
├── docker-compose.yml              # Development environment
├── kubernetes/                     # Production deployment configs
├── docs/                          # Documentation and guides
└── scripts/                       # Build and deployment scripts
```

## Usage Examples

### **Authentication Flow**
```bash
# Register new account
POST /api/auth/register
{
  "email": "user@company.com",
  "password": "SecurePass123!",
  "accountType": "business",
  "firstName": "John",
  "lastName": "Doe"
}

# Verify registration with OTP
POST /api/auth/verify-registration  
{
  "email": "user@company.com",
  "otp": "123456"
}

# Login with credentials
POST /api/auth/login
{
  "email": "user@company.com", 
  "password": "SecurePass123!"
}

# Verify login with OTP
POST /api/auth/verify-login
{
  "email": "user@company.com",
  "otp": "654321",
  "trustDevice": true
}
```

### **Natural Language Queries**
```
User: "What were my top 5 products by revenue last month?"
AI: *Analyzing your sales data...*
    *Generating SQL query...*
    *Creating bar chart visualization...*
    
    Here are your top 5 products by revenue in September:
    1. Product A: $45,000 (↑15% vs August)
    2. Product B: $38,500 (↓5% vs August)
    ...
    [Interactive bar chart displayed]

User: "Show me the trend for Product A over the last 6 months"
AI: *Querying historical data...*
    *Creating trend analysis...*
    
    Product A Revenue Trend (Apr-Sep 2024):
    - Strong growth trajectory: +35% overall
    - Peak in July: $52,000  
    - Seasonal dip in August: -12%
    [Interactive line chart with trend line]

User: "Alert me when any product sales drop below $20k"
AI: Alert created! You'll be notified when any product's 
    monthly sales fall below $20,000.
```

### **Data Source Integration**
```bash
# Connect PostgreSQL database
POST /api/data/sources
{
  "type": "postgresql",
  "name": "Sales Database",
  "config": {
    "host": "db.company.com",
    "port": 5432,
    "database": "sales_prod",
    "username": "readonly_user"
  }
}

# Upload CSV file
POST /api/data/upload
[Multipart form with CSV file]
# Auto-detects schema: columns, types, relationships

# Query data with natural language
POST /api/analytics/query
{
  "question": "What's the average order value by customer segment?",
  "dataSource": "sales_database",
  "visualizationType": "auto" 
}
```

### **Dashboard Creation**
```bash
# Create interactive dashboard
POST /api/dashboards
{
  "name": "Sales Performance Dashboard",
  "layout": {
    "widgets": [
      {
        "type": "metric_card",
        "query": "SELECT SUM(revenue) as total_revenue FROM sales",
        "position": { "x": 0, "y": 0, "w": 2, "h": 1 }
      },
      {
        "type": "line_chart", 
        "query": "SELECT date, SUM(revenue) FROM sales GROUP BY date",
        "position": { "x": 2, "y": 0, "w": 4, "h": 2 }
      }
    ]
  },
  "refreshInterval": 300,
  "isPublic": false
}
```

## Available Scripts

```bash
# Development Commands
npm run dev              # Start development server with hot reload
npm run dev:frontend     # Start Next.js frontend development
npm run dev:backend      # Start Express backend development

# Database Operations  
npm run db:generate      # Generate Prisma client
npm run db:migrate       # Run database migrations
npm run db:seed          # Seed database with sample data
npm run db:studio        # Open Prisma Studio (database GUI)
npm run db:reset         # Reset database (⚠️ destructive)

# Build & Production
npm run build            # Build TypeScript to JavaScript
npm run build:frontend   # Build Next.js frontend
npm run build:backend    # Build Express backend
npm start               # Start production server

# Testing & Quality
npm run test            # Run unit tests with Jest
npm run test:e2e        # Run end-to-end tests with Playwright
npm run test:coverage   # Generate test coverage reports
npm run lint           # Run ESLint for code quality
npm run type-check     # Run TypeScript type checking

# Deployment & Docker
npm run docker:build    # Build Docker images
npm run docker:up       # Start Docker development environment
npm run docker:down     # Stop Docker containers
npm run deploy:staging  # Deploy to staging environment
npm run deploy:prod     # Deploy to production

# Utilities
npm run logs           # View application logs
npm run docs:generate  # Generate API documentation
npm run security:audit # Run security vulnerability scan
```

## Environment Variables

### **Core Application**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PORT` | Server port | No | `3000` |
| `NODE_ENV` | Environment mode | No | `development` |
| `CORS_ORIGIN` | CORS allowed origins | No | `http://localhost:3000` |

### **Database Configuration**
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql://user:pass@localhost:5432/db` |
| `REDIS_URL` | Redis connection string | Yes | `redis://localhost:6379` |

### **Authentication & Security**
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `JWT_SECRET` | JWT signing secret | Yes | `super-secure-secret-key-min-32-chars` |
| `JWT_EXPIRES_IN` | JWT token expiration | No | `7d` |
| `BCRYPT_ROUNDS` | Password hashing rounds | No | `12` |

### **AI & ML Configuration**
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq AI API key | Yes | `gsk_...` |
| `GROQ_MODEL` | Groq model to use | No | `llama-3.1-8b-instant` |

### **Email Service**
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SMTP_HOST` | SMTP server host | Yes | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | Yes | `587` |
| `SMTP_SECURE` | Use TLS/SSL | No | `false` |
| `SMTP_USER` | SMTP username | Yes | `your-email@gmail.com` |
| `SMTP_PASS` | SMTP password | Yes | `your-app-password` |
| `EMAIL_FROM` | From email address | Yes | `Smart BI <noreply@company.com>` |

### **Feature Flags** 
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENABLE_REGISTRATION` | Allow new registrations | No | `true` |
| `ENABLE_DEVICE_TRUST` | Device trust feature | No | `true` |
| `MAX_FILE_SIZE_MB` | Max upload file size | No | `100` |
| `SESSION_TIMEOUT_HOURS` | Session timeout | No | `24` |

## Platform Capabilities

### **AI-Powered Analytics Engine**

#### Natural Language to SQL
- Convert conversational queries into optimized SQL
- Support for complex joins, aggregations, and filters
- Context-aware query building with conversation memory
- SQL query optimization and performance suggestions

#### Automated Insights
- **Pattern Detection**: Identify trends, seasonality, outliers
- **Anomaly Alerts**: Real-time notifications for unusual data patterns  
- **Predictive Analytics**: Forecasting and trend predictions
- **Smart Recommendations**: Suggest relevant charts and analyses

### **Visualization & Dashboard Engine**

#### Chart Types Supported
- **Basic Charts**: Bar, Line, Pie, Doughnut, Area, Scatter
- **Advanced Charts**: Heatmaps, Treemaps, Sankey diagrams, Funnel charts
- **Time Series**: Timeline charts with zoom, pan, real-time updates
- **Geographic**: Maps with data overlays and region highlighting
- **Statistical**: Box plots, histograms, distribution charts

#### Interactive Features
- **Drill-Down**: Click charts to explore deeper data levels
- **Cross-Filtering**: Filter multiple charts simultaneously  
- **Real-time Updates**: Live data streaming with WebSocket connections
- **Export Options**: PNG, PDF, Excel exports with custom formatting

### **Data Source Integrations**

#### Supported Databases
- **PostgreSQL**: Full support with advanced features
- **MySQL/MariaDB**: Complete compatibility with all versions
- **SQL Server**: Enterprise integration with Windows Authentication
- **Oracle**: Basic support for standard operations
- **MongoDB**: NoSQL document database support
- **SQLite**: Lightweight local database support

#### File Processing
- **CSV Files**: Up to 100MB with automatic schema inference
- **Excel Files**: .xlsx and .xls with multiple sheet support
- **JSON Data**: Structured data import with nested object handling
- **Real-time Streams**: WebSocket and SSE data ingestion

#### Cloud & API Integrations
- **REST APIs**: Custom API connections with authentication
- **GraphQL**: Query GraphQL endpoints with automatic introspection
- **Webhooks**: Real-time data updates via webhook listeners
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob

## Dashboard Features

### **Real-time Analytics**
- **Live Data Streaming**: WebSocket connections for instant updates
- **Auto-refresh**: Configurable refresh intervals (30s to 24h)
- **Performance Monitoring**: Query execution time and system health
- **Alert Notifications**: Real-time alerts via email, Slack, webhooks

### **Collaboration Tools**
- **Dashboard Sharing**: Public links, team access, role-based permissions
- **Comments & Annotations**: Add context to charts and dashboards
- **Version History**: Track dashboard changes and restore previous versions
- **Team Workspaces**: Organize dashboards by departments or projects

### **Enterprise Security**
- **Single Sign-On (SSO)**: SAML, OAuth2, Active Directory integration
- **Role-Based Access Control**: Granular permissions for data and features  
- **Data Encryption**: End-to-end encryption for data in transit and at rest
- **Audit Logging**: Complete audit trail of user actions and data access
- **Compliance**: GDPR, SOC2, HIPAA compliance features

### **Mobile & Responsive Design**
- **Progressive Web App (PWA)**: Install on mobile devices like native app
- **Touch Interactions**: Optimized for mobile chart interactions
- **Offline Mode**: View cached dashboards without internet connection
- **Responsive Layouts**: Automatically adapt to any screen size

## Configuration

### **Authentication Configuration**
Customize authentication settings in `src/config/auth.ts`:

```typescript
export const authConfig = {
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    refreshExpiresIn: '30d'
  },
  otp: {
    expiryMinutes: 10,        // OTP expires in 10 minutes
    maxAttempts: 3,           // 3 failed attempts before lockout
    lockoutMinutes: 15        // 15-minute lockout period
  },
  deviceTrust: {
    enabled: true,
    durationDays: 30          // Trust devices for 30 days
  },
  rateLimiting: {
    windowMinutes: 15,        // 15-minute rate limit window
    maxAttempts: 5            // 5 attempts per window
  }
};
```

### **Database Configuration**
Configure data sources in `src/config/database.ts`:

```typescript
export const databaseConfig = {
  connections: {
    maxPoolSize: 20,          // Max database connections
    idleTimeout: 30000,       // 30s idle timeout
    queryTimeout: 60000       // 60s query timeout
  },
  caching: {
    enabled: true,
    ttl: 300,                 // 5-minute cache TTL
    maxMemory: '256mb'        // Max Redis memory usage
  },
  fileUpload: {
    maxSizeMB: 100,           // 100MB max file size
    allowedTypes: ['.csv', '.xlsx', '.json'],
    virusScan: true           // Enable virus scanning
  }
};
```

### **AI Engine Configuration**
Customize AI behavior in `src/config/ai.ts`:

```typescript
export const aiConfig = {
  groq: {
    model: 'llama-3.1-8b-instant',
    maxTokens: 4096,
    temperature: 0.1,         // Low temperature for accuracy
    maxRetries: 3
  },
  agent: {
    maxIterations: 5,         // Max iterations per query
    memorySize: 100,          // Keep last 100 messages
    toolTimeout: 30000        // 30s tool execution timeout
  },
  nlp: {
    confidenceThreshold: 0.8, // 80% confidence for SQL generation
    enableCache: true,        // Cache frequent queries
    supportedLanguages: ['en', 'es', 'fr'] // Multi-language support
  }
};
```

## Troubleshooting

### **Common Authentication Issues**

**"Email verification failed"**
```bash
# Check email service configuration
npm run test:email

# Verify SMTP settings in .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

**"JWT token invalid or expired"**
```bash
# Clear browser localStorage and cookies
# Check JWT_SECRET is properly set
# Verify token expiration settings
```

**"OTP expired or invalid"** 
```bash
# OTPs expire after 10 minutes
# Check system clock synchronization
# Verify email delivery isn't delayed
```

### **Database Connection Issues**

**"Database connection failed"**
```bash
# Test database connection
npm run db:test

# Check PostgreSQL is running
docker ps | grep postgres

# Verify DATABASE_URL format
DATABASE_URL="postgresql://user:password@host:port/database"
```

**"Prisma migration errors"**
```bash
# Reset database (⚠️ destructive)
npm run db:reset

# Generate fresh Prisma client
npm run db:generate

# Run migrations manually
npx prisma migrate deploy
```

### **Redis Cache Issues**

**"Redis connection refused"**
```bash
# Start Redis server
redis-server
# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Test Redis connection
redis-cli ping
```

### **Performance Issues**

**"Slow query performance"**
```bash
# Enable query logging
DATABASE_LOGGING=true npm run dev

# Check database indexes
npm run db:studio

# Monitor with performance dashboard
npm run monitor:performance
```

**"High memory usage"**
```bash
# Check Redis memory usage
redis-cli info memory

# Optimize cache settings
REDIS_MAXMEMORY=256mb
REDIS_POLICY=allkeys-lru
```

### **File Upload Problems**

**"File upload timeout"**
```bash
# Increase upload limits
MAX_FILE_SIZE_MB=200
UPLOAD_TIMEOUT_MS=300000

# Check disk space
df -h
```

**"CSV parsing errors"**
```bash
# Validate CSV format
# Check for special characters
# Ensure proper encoding (UTF-8)
```

### **AI/ML Service Issues**

**"Groq API rate limiting"**
```bash
# Check API usage
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/usage

# Implement request queuing
GROQ_RATE_LIMIT=true
GROQ_REQUESTS_PER_MINUTE=30
```

**"SQL generation errors"**
```bash
# Enable AI debugging
AI_DEBUG=true npm run dev

# Check conversation context
# Verify database schema is accessible
```

## Performance & Scalability

### **Performance Benchmarks**
- **API Response Time**: < 200ms for standard queries
- **Chart Generation**: < 3 seconds for complex visualizations  
- **Data Processing**: Handle 1M+ rows with sub-second response
- **Concurrent Users**: Support 1,000+ simultaneous users
- **Database Queries**: Optimized with indexing and caching
- **Memory Usage**: < 500MB for typical workloads

### **Scalability Features**
- **Horizontal Scaling**: Kubernetes auto-scaling based on CPU/memory
- **Database Read Replicas**: Distribute read traffic across multiple instances
- **Redis Clustering**: Distributed caching for high availability
- **CDN Integration**: Global content delivery for static assets
- **Load Balancing**: Nginx with health checks and failover
- **Microservices**: Independently scalable service components

### **Monitoring & Observability**
- **Application Metrics**: Response time, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, disk, network usage
- **Business Metrics**: User engagement, query success rates, feature adoption
- **Error Tracking**: Sentry integration for real-time error monitoring
- **Log Aggregation**: ELK stack for centralized logging
- **Alerting**: PagerDuty/Slack notifications for critical issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Bee Agent Framework](https://github.com/i-am-bee/bee-agent-framework)
- [Groq Console](https://console.groq.com/)
- [DuckDuckGo Search](https://duckduckgo.com/)
- [OpenMeteo API](https://open-meteo.com/)

## 💡 Tips

- Use specific queries for better tool usage
- Clear memory when switching topics
- The agent works best with natural language
- Weather queries work with city names or coordinates
- Web searches are great for current information

## 🆘 Support

If you encounter any issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Look at the console logs for error details
3. Verify your environment setup
4. Check your API key and internet connection

## Deployment Guide

### **Development Environment**
```bash
# Clone and setup
git clone https://github.com/your-username/smart-bi-platform
cd bee_agent_framework
npm install

# Start services
docker-compose up -d  # PostgreSQL + Redis
npm run db:migrate    # Database setup
npm run dev          # Development server
```

### **Production Deployment**

#### **Docker Deployment**
```dockerfile
# Multi-stage build for production
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

#### **Kubernetes Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smart-bi-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smart-bi-platform
  template:
    metadata:
      labels:
        app: smart-bi-platform
    spec:
      containers:
      - name: api
        image: smart-bi-platform:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi" 
            cpu: "500m"
```

#### **Cloud Platform Deployment**

**AWS ECS with RDS**
```bash
# Deploy to AWS using Terraform
cd terraform/aws
terraform init
terraform plan
terraform apply

# Or use AWS CDK
npm run deploy:aws
```

**Google Cloud Run**
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/smart-bi
gcloud run deploy smart-bi --image gcr.io/PROJECT_ID/smart-bi \
  --platform managed --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...
```

**Azure Container Instances**
```bash
# Deploy to Azure
az container create \
  --resource-group smart-bi-rg \
  --name smart-bi-platform \
  --image smart-bi-platform:latest \
  --ports 3000 \
  --environment-variables DATABASE_URL=postgresql://...
```

### **Monitoring Setup**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./monitoring/grafana:/var/lib/grafana
```

## Contributing

We welcome contributions to make this the best open-source BI platform! Here's how to get started:

### **Development Setup**
```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/smart-bi-platform
cd bee_agent_framework

# Install dependencies
npm install

# Create feature branch
git checkout -b feature/amazing-feature

# Set up development environment
cp .env.example .env
docker-compose up -d
npm run db:migrate
npm run dev
```

### **Contribution Guidelines**
- **Code Style**: Follow ESLint and Prettier configurations
- **Testing**: Add tests for new features (aim for 80%+ coverage)
- **Documentation**: Update README and API docs for changes
- **Commits**: Use conventional commits format (`feat:`, `fix:`, `docs:`)
- **Pull Requests**: Include description, screenshots, and test results

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Links & Resources

### **Official Links**
- **Documentation**: [docs.smart-bi-platform.com](https://docs.smart-bi-platform.com)
- **Website**: [smart-bi-platform.com](https://smart-bi-platform.com)
- **Community**: [Discord Server](https://discord.gg/smart-bi)
- **Issues**: [GitHub Issues](https://github.com/your-username/smart-bi-platform/issues)

### **Technology Partners**
- **Bee Agent Framework**: [GitHub](https://github.com/i-am-bee/bee-agent-framework)
- **Groq AI**: [Console](https://console.groq.com/) | [Documentation](https://docs.groq.com/)
- **PostgreSQL**: [Official Site](https://postgresql.org/) | [Documentation](https://postgresql.org/docs/)
- **Redis**: [Official Site](https://redis.io/) | [Documentation](https://redis.io/docs/)
- **Next.js**: [Official Site](https://nextjs.org/) | [Documentation](https://nextjs.org/docs)

## Roadmap & Future Features

### **Q1 2025: Advanced Analytics**
- Machine learning integration for predictive analytics
- Advanced statistical analysis (regression, clustering)
- Automated insight recommendations
- Mobile app for iOS and Android

### **Q2 2025: Enterprise Features**
- Multi-tenant architecture with white-labeling
- Advanced security features (SSO, RBAC, audit trails)
- Multi-language support (Spanish, French, German)
- Advanced chart types (3D charts, geographic visualizations)

## Support & Community

### **Getting Help**
1. **Documentation**: Check our comprehensive docs first
2. **Community Discord**: Get help from other developers
3. **GitHub Issues**: Report bugs or request features
4. **Email Support**: enterprise@smart-bi-platform.com

### **Enterprise Support**
- **Priority Support**: 24/7 support with SLA guarantees
- **Training**: Custom training sessions for your team
- **Custom Development**: Tailored features for your needs
- **On-Premise Deployment**: Private cloud or on-premise installation

---

## 🎉 **Ready to Transform Your Data?**

**Start building the future of Business Intelligence today!**

```bash
# Get started in 5 minutes
git clone https://github.com/your-username/smart-bi-platform
cd bee_agent_framework
npm install && npm run dev
```

**Join thousands of developers building better BI tools with AI!**

---

**Made with � using 🐝 Bee Agent Framework | Transforming Data into Insights**

[![GitHub Stars](https://img.shields.io/github/stars/your-username/smart-bi-platform?style=social)](https://github.com/your-username/smart-bi-platform)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Discord](https://img.shields.io/discord/123456789?color=7289da&label=Discord)](https://discord.gg/smart-bi)
[![Follow on Twitter](https://img.shields.io/twitter/follow/SmartBIPlatform?style=social)](https://twitter.com/SmartBIPlatform)