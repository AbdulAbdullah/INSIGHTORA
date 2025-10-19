import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { fileURLToPath } from 'url';
import { BeeAgentService } from './BeeAgentService.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;

// Serve static files
app.use(express.static(path.join(__dirname, '../public')));

// Create agent service instance
const agentService = new BeeAgentService();

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('🔌 User connected');

  socket.on('chat_message', async (data) => {
    const { message } = data;
    console.log('💬 Received message:', message);

    try {
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

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 Bee Agent Chat Server running on http://localhost:${PORT}`);
  console.log(`🤖 Agent ready with Groq LLaMA 3.1 8B`);
  console.log(`🛠️  Tools available: DuckDuckGo Search, OpenMeteo Weather`);
});