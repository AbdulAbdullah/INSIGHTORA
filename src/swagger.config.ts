import swaggerJsdoc from 'swagger-jsdoc';
import { SwaggerUiOptions } from 'swagger-ui-express';

const options: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Smart Business Intelligence Assistant API',
      version: '1.0.0',
      description: `
        A comprehensive Business Intelligence Assistant API powered by AI agent framework.
        
        Features:
        - AI-powered data analysis and insights
        - CSV/Excel file upload and processing
        - Interactive chat interface with real-time updates
        - Data visualization and chart generation
        - Business metrics calculation and reporting
        - Natural language query processing for data
        
        This API provides both REST endpoints and WebSocket connections for real-time communication.
      `,
      contact: {
        name: 'BI Assistant Support',
        email: 'support@biassistant.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server'
      },
      {
        url: 'https://your-app.onrender.com',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        BearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'Enter JWT access token'
        },
        ApiKeyAuth: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key'
        }
      },
      schemas: {
        ChatMessage: {
          type: 'object',
          required: ['message'],
          properties: {
            message: {
              type: 'string',
              description: 'The chat message content',
              example: 'Analyze the sales data trends for Q4'
            },
            sessionId: {
              type: 'string',
              description: 'Optional session identifier for conversation continuity'
            }
          }
        },
        ChatResponse: {
          type: 'object',
          properties: {
            response: {
              type: 'string',
              description: 'AI assistant response'
            },
            sessionId: {
              type: 'string',
              description: 'Session identifier'
            },
            timestamp: {
              type: 'string',
              format: 'date-time',
              description: 'Response timestamp'
            }
          }
        },
        DataAnalysis: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'Analysis identifier'
            },
            fileName: {
              type: 'string',
              description: 'Original file name'
            },
            rowCount: {
              type: 'integer',
              description: 'Number of data rows processed'
            },
            columns: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Column names in the dataset'
            },
            summary: {
              type: 'object',
              description: 'Statistical summary of the data'
            },
            insights: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'AI-generated insights about the data'
            },
            createdAt: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        ChartConfiguration: {
          type: 'object',
          required: ['type', 'data'],
          properties: {
            type: {
              type: 'string',
              enum: ['line', 'bar', 'pie', 'scatter', 'area'],
              description: 'Chart type'
            },
            data: {
              type: 'object',
              description: 'Chart data configuration'
            },
            options: {
              type: 'object',
              description: 'Chart styling and behavior options'
            },
            title: {
              type: 'string',
              description: 'Chart title'
            }
          }
        },
        User: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: 'User ID'
            },
            email: {
              type: 'string',
              format: 'email',
              description: 'User email address'
            },
            firstName: {
              type: 'string',
              description: 'User first name'
            },
            lastName: {
              type: 'string',
              description: 'User last name'
            },
            accountType: {
              type: 'string',
              enum: ['individual', 'business'],
              description: 'Account type'
            },
            businessName: {
              type: 'string',
              description: 'Business name (for business accounts)'
            },
            displayName: {
              type: 'string',
              description: 'Display name (business name or full name)'
            },
            isVerified: {
              type: 'boolean',
              description: 'Whether the account is verified'
            },
            createdAt: {
              type: 'string',
              format: 'date-time',
              description: 'Account creation timestamp'
            },
            lastLogin: {
              type: 'string',
              format: 'date-time',
              description: 'Last login timestamp'
            }
          }
        },
        AuthTokens: {
          type: 'object',
          properties: {
            accessToken: {
              type: 'string',
              description: 'JWT access token for API authentication'
            },
            refreshToken: {
              type: 'string',  
              description: 'JWT refresh token for token renewal'
            }
          }
        },
        RegisterRequest: {
          type: 'object',
          required: ['email', 'password', 'firstName', 'lastName', 'accountType'],
          properties: {
            email: {
              type: 'string',
              format: 'email',
              example: 'user@example.com'
            },
            password: {
              type: 'string',
              minLength: 8,
              example: 'SecurePass123',
              description: 'Must be at least 8 characters with uppercase, lowercase, and number'
            },
            firstName: {
              type: 'string',
              minLength: 2,
              maxLength: 50,
              example: 'John'
            },
            lastName: {
              type: 'string',
              minLength: 2,
              maxLength: 50,
              example: 'Doe'
            },
            accountType: {
              type: 'string',
              enum: ['individual', 'business'],
              example: 'individual'
            },
            businessName: {
              type: 'string',
              maxLength: 100,
              example: 'Acme Corporation',
              description: 'Required if accountType is business'
            }
          }
        },
        LoginRequest: {
          type: 'object',
          required: ['email', 'password'],
          properties: {
            email: {
              type: 'string',
              format: 'email',
              example: 'user@example.com'
            },
            password: {
              type: 'string',
              example: 'SecurePass123'
            }
          }
        },
        OTPVerificationRequest: {
          type: 'object',
          required: ['email', 'otp'],
          properties: {
            email: {
              type: 'string',
              format: 'email',
              example: 'user@example.com'
            },
            otp: {
              type: 'string',
              pattern: '^\\d{6}$',
              example: '123456',
              description: '6-digit verification code'
            }
          }
        },
        AuthResponse: {
          type: 'object',
          properties: {
            message: {
              type: 'string',
              description: 'Success message'
            },
            user: {
              $ref: '#/components/schemas/User'
            },
            tokens: {
              $ref: '#/components/schemas/AuthTokens'
            },
            timestamp: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        ErrorResponse: {
          type: 'object',
          properties: {
            error: {
              type: 'string',
              description: 'Error message'
            },
            code: {
              type: 'string',
              description: 'Error code'
            },
            timestamp: {
              type: 'string',
              format: 'date-time'
            }
          }
        },
        HealthCheck: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              enum: ['healthy', 'unhealthy'],
              description: 'Service health status'
            },
            timestamp: {
              type: 'string',
              format: 'date-time'
            },
            version: {
              type: 'string',
              description: 'API version'
            },
            services: {
              type: 'object',
              properties: {
                database: {
                  type: 'string',
                  enum: ['connected', 'disconnected', 'not_configured']
                },
                ai_agent: {
                  type: 'string',
                  enum: ['ready', 'loading', 'error']
                }
              }
            }
          }
        }
      },
      responses: {
        BadRequest: {
          description: 'Bad request - invalid input parameters',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/ErrorResponse'
              }
            }
          }
        },
        Unauthorized: {
          description: 'Unauthorized - invalid or missing API key',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/ErrorResponse'
              }
            }
          }
        },
        InternalError: {
          description: 'Internal server error',
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/ErrorResponse'
              }
            }
          }
        }
      }
    },
    tags: [
      {
        name: 'Authentication',
        description: 'User registration, login, and account management'
      },
      {
        name: 'Health',
        description: 'System health and status endpoints'
      },
      {
        name: 'Chat',
        description: 'AI chat and conversation endpoints'
      },
      {
        name: 'Data Upload',
        description: 'File upload and data ingestion'
      },
      {
        name: 'Analytics',
        description: 'Data analysis and business intelligence'
      },
      {
        name: 'Visualization',
        description: 'Chart generation and data visualization'
      },
      {
        name: 'User Management',
        description: 'User profile and account management'
      },
      {
        name: 'Testing',
        description: 'Test endpoints that work without database connection'
      }
    ]
  },
  apis: [
    './src/routes/*.ts',
    './src/server.ts'
  ],
};

export const swaggerSpec = swaggerJsdoc(options);

export const swaggerUiOptions: SwaggerUiOptions = {
  customCss: `
    .swagger-ui .topbar { display: none; }
    .swagger-ui .scheme-container { margin: 0; padding: 20px 0; }
    .swagger-ui .info { margin: 20px 0; }
    .swagger-ui .info .title { color: #2c3e50; }
  `,
  customSiteTitle: 'BI Assistant API Documentation',
  customfavIcon: '/favicon.ico',
  swaggerOptions: {
    defaultModelsExpandDepth: 2,
    defaultModelExpandDepth: 2,
    docExpansion: 'list',
    filter: true,
    showRequestHeaders: true,
    tryItOutEnabled: true
  }
};