import "dotenv/config";
import { BeeAgentService } from "./BeeAgentService.js";

async function runTest(testName: string, testFn: () => Promise<void>): Promise<boolean> {
    try {
        console.log(`📝 ${testName}`);
        await testFn();
        console.log(`✅ ${testName} - PASSED`);
        console.log('');
        return true;
    } catch (error) {
        console.log(`❌ ${testName} - FAILED`);
        console.log(`Error: ${error.message}`);
        console.log('');
        return false;
    }
}

async function testBeeAgent() {
    console.log('🧪 Starting Bee Agent Test Suite...');
    console.log('');

    // Initialize the agent service
    const agentService = new BeeAgentService();
    let passedTests = 0;
    let totalTests = 0;

    // Test 1: Basic Conversation
    totalTests++;
    const test1Passed = await runTest("Test 1: Basic Conversation", async () => {
        const response = await agentService.chat("Hello! How are you?", (update) => {
            console.log(`  ${update.type}: ${update.content.substring(0, 100)}${update.content.length > 100 ? '...' : ''}`);
        });
        console.log(`  Response: ${response.substring(0, 150)}${response.length > 150 ? '...' : ''}`);
    });
    if (test1Passed) passedTests++;

    // Test 2: Weather Query
    totalTests++;
    const test2Passed = await runTest("Test 2: Weather Query", async () => {
        const response = await agentService.chat("What's the weather like in London?", (update) => {
            console.log(`  ${update.type}: ${update.content.substring(0, 100)}${update.content.length > 100 ? '...' : ''}`);
        });
        console.log(`  Response: ${response.substring(0, 150)}${response.length > 150 ? '...' : ''}`);
    });
    if (test2Passed) passedTests++;

    // Test 3: Simple Web Search (safer query)
    totalTests++;
    const test3Passed = await runTest("Test 3: Web Search", async () => {
        const response = await agentService.chat("Search for information about TypeScript programming language", (update) => {
            console.log(`  ${update.type}: ${update.content.substring(0, 100)}${update.content.length > 100 ? '...' : ''}`);
        });
        console.log(`  Response: ${response.substring(0, 150)}${response.length > 150 ? '...' : ''}`);
    });
    if (test3Passed) passedTests++;

    // Test 4: Memory Management
    totalTests++;
    const test4Passed = await runTest("Test 4: Memory Management", async () => {
        await agentService.clearMemory();
        console.log('  Memory cleared successfully');
        
        const response = await agentService.chat("Do you remember what we talked about before?", (update) => {
            console.log(`  ${update.type}: ${update.content.substring(0, 100)}${update.content.length > 100 ? '...' : ''}`);
        });
        console.log(`  Response: ${response.substring(0, 150)}${response.length > 150 ? '...' : ''}`);
    });
    if (test4Passed) passedTests++;

    // Summary
    console.log('📊 Test Results:');
    console.log(`✅ Passed: ${passedTests}/${totalTests}`);
    console.log(`❌ Failed: ${totalTests - passedTests}/${totalTests}`);
    
    if (passedTests === totalTests) {
        console.log('🎉 All tests passed successfully!');
    } else {
        console.log('⚠️  Some tests failed. Check the logs above for details.');
        console.log('💡 Note: Occasional failures can happen due to network issues or API rate limits.');
    }
}

// Run the test
testBeeAgent();