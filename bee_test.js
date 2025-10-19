import "dotenv/config";
import { BeeAgent } from "bee-agent-framework/agents/bee/agent";
import { GroqChatModel } from "bee-agent-framework/adapters/groq/backend/chat";
import { TokenMemory } from "bee-agent-framework/memory/tokenMemory";
import { DuckDuckGoSearchTool } from "bee-agent-framework/tools/search/duckDuckGoSearch";
import { OpenMeteoTool } from "bee-agent-framework/tools/weather/openMeteo";

const llm = new GroqChatModel("llama-3.1-8b-instant", {
    temperature: 0.7,
    maxTokens: 2000
});
const memory = new TokenMemory();
const tools = [new DuckDuckGoSearchTool(), new OpenMeteoTool()];

const agent = new BeeAgent({ 
    llm,
    memory,
    tools
});

const response = await agent
    .run({ prompt: "What's the weather like in Kano State?" })
    .observe((emitter) => {
        emitter.on("update", async ({ data, update, meta }) => {
            console.log(`Agent (${update.key}) 🤖 : `, update.value);
        });
    });

console.log(`Agent 🤖 : `, response.result.text);