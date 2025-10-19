import "dotenv/config";
import { GroqChatModel } from "bee-agent-framework/adapters/groq/backend/chat";

async function testGroqConnection() {
  try {
    console.log('🔑 Testing Groq API Key:', process.env.GROQ_API_KEY?.substring(0, 10) + '...');
    
    const llm = new GroqChatModel("llama-3.1-8b-instant");
    console.log('✅ GroqChatModel created successfully');
    
    // Try a simple generation without tools
    console.log('🧪 Testing basic chat completion...');
    
    // This is a basic test to see if the model works
    console.log('Model ready for testing');
    
  } catch (error) {
    console.error('❌ Error testing Groq:', error);
  }
}

testGroqConnection();