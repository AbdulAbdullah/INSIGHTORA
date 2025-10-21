import "dotenv/config";
import { BeeAgent } from "bee-agent-framework/agents/bee/agent";
import { GroqChatModel } from "bee-agent-framework/adapters/groq/backend/chat";
import { UnconstrainedMemory } from "bee-agent-framework/memory/unconstrainedMemory";
import { DuckDuckGoSearchTool } from "bee-agent-framework/tools/search/duckDuckGoSearch";
import { OpenMeteoTool } from "bee-agent-framework/tools/weather/openMeteo";
import * as fs from 'fs/promises';
import * as path from 'path';
import Papa from 'papaparse';

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

export interface DataAnalysisResult {
  id: string;
  fileName: string;
  rowCount: number;
  columns: string[];
  summary: {
    [key: string]: {
      type: string;
      count: number;
      unique?: number;
      mean?: number;
      median?: number;
      std?: number;
      min?: number;
      max?: number;
      nullCount: number;
    };
  };
  insights: string[];
  createdAt: Date;
}

export interface UserContext {
  userId: string;
  email: string;
  accountType: string;
  displayName: string;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'area';
  title: string;
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string;
      borderWidth?: number;
    }>;
  };
  options?: any;
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

      console.log('BeeAgent initialized successfully');
    } catch (error) {
      console.error('Error initializing BeeAgent:', error);
      throw error;
    }
  }

  async chat(message: string, onUpdate?: (update: AgentUpdate) => void, userContext?: UserContext): Promise<string> {
    try {
      console.log('Processing message:', message);
      
      // Enhanced prompt with user context
      let enhancedMessage = message;
      if (userContext) {
        enhancedMessage = `User Context: ${userContext.displayName} (${userContext.accountType} account)\n\nUser Question: ${message}`;
      }
      
      const response = await this.agent
        .run({ prompt: enhancedMessage })
        .observe((emitter) => {
          emitter.on("update", async ({ data, update, meta }) => {
            console.log('Agent update:', update.key, '=', update.value);
            if (onUpdate) {
              onUpdate({
                type: update.key as any,
                content: update.value
              });
            }
          });
        });

      console.log('Agent response:', response.result.text);
      return response.result.text;
    } catch (error) {
      console.error('Detailed Agent error:', error);
      
      // Check if it's an API key issue
      if (error.message && error.message.includes('API key')) {
        throw new Error('API key issue. Please check your Groq API key in the .env file.');
      }
      
      // Check if it's a network issue
      if (error.message && (error.message.includes('ECONNREFUSED') || error.message.includes('fetch'))) {
        throw new Error('Network error. Please check your internet connection.');
      }
      
      // Generic error with more details
      const errorMessage = error?.errors?.[0]?.errors?.[0]?.message || error.message || 'Unknown error occurred';
      throw new Error(`Agent error: ${errorMessage}. Please try again.`);
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
    
    console.log('Memory cleared and agent reinitialized');
  }

  // Business Intelligence Methods

  async analyzeCSVFile(filePath: string, fileName: string): Promise<DataAnalysisResult> {
    try {
      const fileContent = await fs.readFile(filePath, 'utf-8');
      
      return new Promise((resolve, reject) => {
        Papa.parse(fileContent, {
          header: true,
          skipEmptyLines: true,
          dynamicTyping: true,
          complete: (results) => {
            try {
              const data = results.data as any[];
              const columns = Object.keys(data[0] || {});
              
              // Generate statistical summary
              const summary = this.generateDataSummary(data, columns);
              
              // Create analysis result
              const analysisResult: DataAnalysisResult = {
                id: this.generateId(),
                fileName,
                rowCount: data.length,
                columns,
                summary,
                insights: this.generateDataInsights(data, columns, summary),
                createdAt: new Date()
              };

              console.log(`Data analysis completed for ${fileName}: ${data.length} rows, ${columns.length} columns`);
              resolve(analysisResult);
            } catch (error) {
              reject(error);
            }
          },
          error: (error) => {
            reject(new Error(`CSV parsing error: ${error.message}`));
          }
        });
      });
    } catch (error) {
      console.error('Error analyzing CSV file:', error);
      throw new Error(`Failed to analyze CSV file: ${error.message}`);
    }
  }

  private generateDataSummary(data: any[], columns: string[]): DataAnalysisResult['summary'] {
    const summary: DataAnalysisResult['summary'] = {};

    columns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val !== null && val !== undefined && val !== '');
      const nullCount = data.length - values.length;
      
      if (values.length === 0) {
        summary[column] = {
          type: 'empty',
          count: 0,
          nullCount,
        };
        return;
      }

      const firstValue = values[0];
      const isNumeric = values.every(val => typeof val === 'number' || (!isNaN(parseFloat(val)) && isFinite(val)));
      
      if (isNumeric) {
        const numericValues = values.map(val => typeof val === 'number' ? val : parseFloat(val));
        const sorted = [...numericValues].sort((a, b) => a - b);
        const sum = numericValues.reduce((acc, val) => acc + val, 0);
        const mean = sum / numericValues.length;
        const variance = numericValues.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / numericValues.length;
        
        summary[column] = {
          type: 'numeric',
          count: values.length,
          nullCount,
          mean: Math.round(mean * 100) / 100,
          median: sorted.length % 2 === 0 
            ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2 
            : sorted[Math.floor(sorted.length / 2)],
          std: Math.round(Math.sqrt(variance) * 100) / 100,
          min: Math.min(...numericValues),
          max: Math.max(...numericValues)
        };
      } else {
        const uniqueValues = new Set(values);
        summary[column] = {
          type: 'categorical',
          count: values.length,
          unique: uniqueValues.size,
          nullCount
        };
      }
    });

    return summary;
  }

  private generateDataInsights(data: any[], columns: string[], summary: DataAnalysisResult['summary']): string[] {
    const insights: string[] = [];
    
    // Data quality insights
    const totalColumns = columns.length;
    const numericColumns = Object.values(summary).filter(col => col.type === 'numeric').length;
    const categoricalColumns = Object.values(summary).filter(col => col.type === 'categorical').length;
    
    insights.push(`Dataset contains ${data.length} records across ${totalColumns} columns`);
    insights.push(`Data composition: ${numericColumns} numeric and ${categoricalColumns} categorical columns`);
    
    // Missing data insights
    const columnsWithMissing = Object.entries(summary).filter(([_, col]) => col.nullCount > 0);
    if (columnsWithMissing.length > 0) {
      const totalMissing = columnsWithMissing.reduce((sum, [_, col]) => sum + col.nullCount, 0);
      insights.push(`Data quality concern: ${totalMissing} missing values across ${columnsWithMissing.length} columns`);
    } else {
      insights.push('Data quality: No missing values detected');
    }
    
    // High-level pattern insights
    if (numericColumns > 0) {
      insights.push('Numeric data available for statistical analysis and trend identification');
    }
    
    if (categoricalColumns > 0) {
      insights.push('Categorical data suitable for segmentation and classification analysis');
    }
    
    // Column-specific insights
    Object.entries(summary).forEach(([columnName, stats]) => {
      if (stats.type === 'numeric' && stats.mean !== undefined) {
        if (stats.std !== undefined && stats.mean !== 0) {
          const coefficientOfVariation = stats.std / Math.abs(stats.mean);
          if (coefficientOfVariation > 1) {
            insights.push(`High variability detected in ${columnName} (CV: ${Math.round(coefficientOfVariation * 100)}%)`);
          }
        }
      }
      
      if (stats.type === 'categorical' && stats.unique !== undefined) {
        const uniquenessRatio = stats.unique / stats.count;
        if (uniquenessRatio > 0.9) {
          insights.push(`${columnName} has high cardinality (${stats.unique} unique values) - potential identifier column`);
        }
      }
    });
    
    return insights;
  }

  async generateChart(analysisId: string, chartType: ChartConfig['type'], xColumn: string, yColumn: string, data: any[]): Promise<ChartConfig> {
    try {
      let chartData: ChartConfig['data'];
      
      switch (chartType) {
        case 'bar':
        case 'line':
          chartData = this.createXYChartData(data, xColumn, yColumn);
          break;
        case 'pie':
          chartData = this.createPieChartData(data, xColumn);
          break;
        default:
          throw new Error(`Chart type ${chartType} not supported yet`);
      }
      
      const chartConfig: ChartConfig = {
        type: chartType,
        title: `${yColumn} by ${xColumn}`,
        data: chartData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top' as const,
            },
            title: {
              display: true,
              text: `${yColumn} by ${xColumn}`
            }
          }
        }
      };
      
      console.log(`Generated ${chartType} chart for ${xColumn} vs ${yColumn}`);
      return chartConfig;
    } catch (error) {
      console.error('Error generating chart:', error);
      throw new Error(`Failed to generate chart: ${error.message}`);
    }
  }

  private createXYChartData(data: any[], xColumn: string, yColumn: string): ChartConfig['data'] {
    const labels = data.map(row => String(row[xColumn]));
    const values = data.map(row => Number(row[yColumn]) || 0);
    
    return {
      labels,
      datasets: [{
        label: yColumn,
        data: values,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    };
  }

  private createPieChartData(data: any[], column: string): ChartConfig['data'] {
    const groupCounts = data.reduce((acc, row) => {
      const value = String(row[column]);
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const labels = Object.keys(groupCounts);
    const values = Object.values(groupCounts) as number[];
    
    const colors = [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 205, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)'
    ];
    
    return {
      labels,
      datasets: [{
        label: 'Count',
        data: values,
        backgroundColor: colors.slice(0, labels.length)
      }]
    };
  }

  async chatWithData(message: string, dataContext: DataAnalysisResult, onUpdate?: (update: AgentUpdate) => void, userContext?: UserContext): Promise<string> {
    const contextualPrompt = `
You are a Business Intelligence Assistant analyzing data from "${dataContext.fileName}".

Data Summary:
- Total Records: ${dataContext.rowCount}
- Columns: ${dataContext.columns.join(', ')}
- Key Insights: ${dataContext.insights.join('; ')}

Column Statistics:
${Object.entries(dataContext.summary).map(([col, stats]) => 
  `${col}: ${stats.type} (${stats.count} values, ${stats.nullCount} missing)`
).join('\n')}

User Question: ${message}

Please provide a professional business intelligence analysis based on the data context above. Focus on actionable insights and recommendations.
    `;
    
    return this.chat(contextualPrompt, onUpdate, userContext);
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  validateChatMessage(message: string): boolean {
    if (!message || typeof message !== 'string') {
      return false;
    }
    
    const trimmed = message.trim();
    if (trimmed.length === 0 || trimmed.length > 2000) {
      return false;
    }
    
    return true;
  }
}