import "dotenv/config";
import { BeeAgent } from "bee-agent-framework/agents/bee/agent";
import { GroqChatModel } from "bee-agent-framework/adapters/groq/backend/chat";
import { UnconstrainedMemory } from "bee-agent-framework/memory/unconstrainedMemory";
import { DuckDuckGoSearchTool } from "bee-agent-framework/tools/search/duckDuckGoSearch";
import { OpenMeteoTool } from "bee-agent-framework/tools/weather/openMeteo";

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AgentUpdate {
  type: 'thought' | 'tool_name' | 'tool_input' | 'tool_output' | 'final_answer';
  content: string;
}

export class BeeAgentService {
  private agent: BeeAgent;
  private memory: UnconstrainedMemory;

  constructor() {
    // Check if API key exists
    if (!process.env.GROQ_API_KEY) {
      console.error('❌ GROQ_API_KEY not found in environment variables');
      throw new Error('🔑 Groq API key is required. Please set GROQ_API_KEY in your .env file.');
    }

    try {
      // Create the LLM with basic configuration
      const llm = new GroqChatModel("llama-3.1-8b-instant");

      // Use UnconstrainedMemory which is more reliable for conversational agents
      this.memory = new UnconstrainedMemory();
      const tools = [new DuckDuckGoSearchTool(), new OpenMeteoTool()];

      this.agent = new BeeAgent({ 
        llm,
        memory: this.memory,
        tools,
        // Add some execution parameters to make it more reliable
        execution: {
          maxIterations: 5,
          totalMaxRetries: 2
        }
      });

      console.log('✅ BeeAgent initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing BeeAgent:', error);
      throw error;
    }
  }

  async chat(message: string, onUpdate?: (update: AgentUpdate) => void): Promise<string> {
    try {
      console.log('🤖 Processing message:', message);
      
      const response = await this.agent
        .run({ prompt: message })
        .observe((emitter) => {
          emitter.on("update", async ({ data, update, meta }) => {
            console.log('📊 Agent update:', update.key, '=', update.value);
            if (onUpdate) {
              onUpdate({
                type: update.key as any,
                content: update.value
              });
            }
          });
        });

      console.log('✅ Agent response:', response.result.text);
      return response.result.text;
    } catch (error) {
      console.error('❌ Detailed Agent error:', error);
      
      // Check if it's an API key issue
      if (error.message && error.message.includes('API key')) {
        throw new Error('🔑 API key issue. Please check your Groq API key in the .env file.');
      }
      
      // Check if it's a network issue
      if (error.message && (error.message.includes('ECONNREFUSED') || error.message.includes('fetch'))) {
        throw new Error('🌐 Network error. Please check your internet connection.');
      }
      
      // Generic error with more details
      const errorMessage = error?.errors?.[0]?.errors?.[0]?.message || error.message || 'Unknown error occurred';
      throw new Error(`🚨 Agent error: ${errorMessage}. Please try again.`);
    }
  }

  async clearMemory(): Promise<void> {
    this.memory = new UnconstrainedMemory();
    // Recreate agent with fresh memory
    const llm = new GroqChatModel("llama-3.1-8b-instant");
    const tools = [new DuckDuckGoSearchTool(), new OpenMeteoTool()];
    
    this.agent = new BeeAgent({ 
      llm,
      memory: this.memory,
      tools,
      execution: {
        maxIterations: 5,
        totalMaxRetries: 2
      }
    });
    
    console.log('🧹 Memory cleared and agent reinitialized');
  }
}