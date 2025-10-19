import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { fileURLToPath } from 'url';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { BeeAgentService } from './BeeAgentService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.NODE_ENV === 'production' 
      ? process.env.ALLOWED_ORIGINS?.split(',') || false
      : ["http://localhost:3000", "http://127.0.0.1:3000"],
    methods: ["GET", "POST"],
    credentials: false
  }
});

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      connectSrc: ["'self'", "wss:", "ws:"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  crossOriginEmbedderPolicy: false
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: NODE_ENV === 'production' ? 100 : 1000, // limit each IP to 100 requests per windowMs in production
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api', limiter);
app.use('/health', rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // limit health checks
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve static files
const staticPath = NODE_ENV === 'production' 
  ? path.join(__dirname, 'public')  // In production, public is copied to dist/
  : path.join(__dirname, '../public');
  
app.use(express.static(staticPath));

// Create agent service instance
const agentService = new BeeAgentService();

// Rate limiting for Socket.IO
const socketRateLimit = new Map();

// Input validation helper
function validateChatMessage(message: string): { isValid: boolean; error?: string } {
  if (!message || typeof message !== 'string') {
    return { isValid: false, error: 'Message must be a non-empty string' };
  }
  
  const trimmed = message.trim();
  if (trimmed.length === 0 || trimmed.length > 2000) {
    return { isValid: false, error: 'Message must be between 1 and 2000 characters' };
  }
  
  // Basic content filtering
  const suspiciousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i
  ];
  
  for (const pattern of suspiciousPatterns) {
    if (pattern.test(message)) {
      return { isValid: false, error: 'Message contains suspicious content' };
    }
  }
  
  return { isValid: true };
}

// Socket rate limiting helper
function checkSocketRateLimit(socketId: string): boolean {
  const now = Date.now();
  const userRequests = socketRateLimit.get(socketId) || [];
  
  // Remove requests older than 1 minute
  const recentRequests = userRequests.filter((time: number) => now - time < 60000);
  
  if (recentRequests.length >= 20) { // Max 20 requests per minute per socket
    return false;
  }
  
  recentRequests.push(now);
  socketRateLimit.set(socketId, recentRequests);
  return true;
}

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('🔌 User connected');

  socket.on('chat_message', async (data) => {
    try {
      // Rate limiting check
      if (!checkSocketRateLimit(socket.id)) {
        socket.emit('agent_error', {
          message: 'Rate limit exceeded. Please slow down.',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const { message } = data;
      
      // Input validation
      const validation = validateChatMessage(message);
      if (!validation.isValid) {
        socket.emit('agent_error', {
          message: validation.error || 'Invalid message',
          timestamp: new Date().toISOString()
        });
        return;
      }

      console.log('💬 Processing message from:', socket.id.substring(0, 8));

      // Send typing indicator
      socket.emit('agent_typing', true);

      // Process message with agent
      const response = await agentService.chat(message, (update) => {
        // Don't send final_answer updates to avoid duplicate messages
        if (update.type !== 'final_answer') {
          socket.emit('agent_update', {
            type: update.type,
            content: update.content
          });
        }
      });

      // Send final response
      socket.emit('agent_typing', false);
      socket.emit('agent_response', {
        message: response,
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('❌ Chat error:', error);
      socket.emit('agent_typing', false);
      socket.emit('agent_error', {
        message: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString()
      });
    }
  });

  socket.on('clear_memory', async () => {
    try {
      await agentService.clearMemory();
      socket.emit('memory_cleared');
      console.log('🧹 Memory cleared');
    } catch (error) {
      console.error('❌ Error clearing memory:', error);
    }
  });

  socket.on('disconnect', () => {
    console.log('🔌 User disconnected');
  });
});

// Health check endpoint - minimal info only
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString()
  });
});

// API info endpoint - only in development
if (NODE_ENV !== 'production') {
  app.get('/api/info', (req, res) => {
    res.json({
      name: 'Bee Agent Chat API',
      version: '1.0.0',
      environment: NODE_ENV,
      features: ['web-search', 'weather', 'chat'],
      status: 'running'
    });
  });
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 Bee Agent Chat Server running on http://localhost:${PORT}`);
  console.log(`🤖 Agent ready with Groq LLaMA 3.1 8B`);
  console.log(`🛠️  Tools available: DuckDuckGo Search, OpenMeteo Weather`);
});