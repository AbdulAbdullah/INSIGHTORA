# 🐝 Bee Agent Chat

A modern, interactive chat interface powered by the Bee Agent Framework with Groq's lightning-fast LLaMA 3.1 model. Built with TypeScript, Express, and Socket.IO for real-time conversations.

## ✨ Features

- **🚀 Lightning Fast**: Powered by Groq's LLaMA 3.1 8B Instant model
- **🔍 Web Search**: Real-time web searches using DuckDuckGo
- **🌤️ Weather Data**: Current weather information from OpenMeteo
- **💬 Real-time Chat**: Interactive web interface with Socket.IO
- **🧠 Memory Management**: Persistent conversation context with clear memory option
- **📱 Responsive Design**: Beautiful, mobile-friendly interface
- **🔒 Secure**: Environment-based API key management
- **⚡ TypeScript**: Full TypeScript support with proper type safety

## 🛠️ Tech Stack

- **Backend**: Node.js, Express, TypeScript, Socket.IO
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Framework**: Bee Agent Framework
- **LLM Provider**: Groq (LLaMA 3.1 8B Instant)
- **Tools**: DuckDuckGo Search, OpenMeteo Weather API
- **Development**: tsx for hot reloading

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Groq API key (free tier available)

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd bee_agent_framework
npm install
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Current selection
CURRENT_PROVIDER=groq
```

### 3. Get Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file

### 4. Start Development Server

```bash
npm run dev
```

The server will start on `http://localhost:3000`

### 5. Open Chat Interface

Navigate to `http://localhost:3000` in your browser and start chatting!

## 📁 Project Structure

```
bee_agent_framework/
├── src/
│   ├── BeeAgentService.ts    # Main agent service class
│   ├── server.ts             # Express server with Socket.IO
│   ├── test.ts              # Basic agent testing
│   └── debug.ts             # Debug utilities
├── public/
│   └── index.html           # Chat interface
├── .env                     # Environment variables
├── package.json             # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## 🎯 Usage Examples

### Basic Conversation
```
You: Hello there!
Agent: Hi! How can I assist you today?
```

### Web Search
```
You: What's the latest news about AI?
Agent: *Thinking: I'll search for the latest AI news*
       *Using tool: DuckDuckGoSearch*
       Based on my search, here are the latest AI developments...
```

### Weather Query
```
You: What's the weather like in London?
Agent: *Using tool: OpenMeteo*
       The current weather in London is 15°C with light rain...
```

## 🔧 Available Scripts

```bash
# Development with hot reload
npm run dev

# Build TypeScript to JavaScript
npm run build

# Start production server
npm start

# Run basic agent test
npm run test
```

## 🛡️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | ✅ Yes |
| `GROQ_MODEL` | Model to use (default: llama-3.1-8b-instant) | ❌ No |
| `PORT` | Server port (default: 3000) | ❌ No |

## 🔍 Available Tools

### 1. DuckDuckGo Search
- Real-time web searches
- Current information retrieval
- News and general queries

### 2. OpenMeteo Weather
- Current weather conditions
- Location-based forecasts
- Temperature, humidity, wind data

## 🎨 Chat Interface Features

### Real-time Updates
- See agent thinking process
- Tool usage indicators
- Typing indicators
- Connection status

### Memory Management
- Persistent conversation context
- Clear memory button for fresh starts
- Conversation history maintained

### Responsive Design
- Mobile-friendly interface
- Clean, professional styling
- Smooth animations and transitions

## 🔧 Configuration

### Agent Configuration
The agent can be configured in `src/BeeAgentService.ts`:

```typescript
this.agent = new BeeAgent({ 
  llm,
  memory: this.memory,
  tools,
  execution: {
    maxIterations: 5,      // Max iterations per query
    totalMaxRetries: 2     // Retry attempts on failure
  }
});
```

### Server Configuration
Server settings in `src/server.ts`:

```typescript
const PORT = process.env.PORT || 3000;
```

## 🚨 Troubleshooting

### Common Issues

**"Cannot find module" errors**
```bash
npm install
```

**"GROQ_API_KEY not found"**
- Check your `.env` file exists
- Verify the API key is correctly set
- Restart the development server

**Agent not responding**
- Check your internet connection
- Verify Groq API key is valid
- Check console for error messages

**Port already in use**
```bash
# Kill process on port 3000
npx kill-port 3000
# Or use different port
PORT=3001 npm run dev
```

## 📈 Performance

- **Response Time**: ~200-500ms per query (Groq LLaMA 3.1)
- **Concurrent Users**: Supports multiple simultaneous chats
- **Memory Usage**: Efficient with UnconstrainedMemory
- **Real-time**: Socket.IO for instant updates

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

---

**Made with 🐝 using Bee Agent Framework**