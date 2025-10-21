import { Router, Request, Response } from 'express';
import { BeeAgentService } from '../BeeAgentService.js';
import { AuthMiddleware } from '../middleware/auth.js';

const router = Router();
const agentService = new BeeAgentService();

/**
 * @swagger
 * /api/analytics/chart:
 *   post:
 *     summary: Generate a chart configuration from analysis data
 *     tags: [Analytics]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - analysisId
 *               - chartType
 *               - xColumn
 *               - yColumn
 *               - data
 *             properties:
 *               analysisId:
 *                 type: string
 *                 description: ID of the data analysis
 *               chartType:
 *                 type: string
 *                 enum: [line, bar, pie, scatter, area]
 *                 description: Type of chart to generate
 *               xColumn:
 *                 type: string
 *                 description: Column name for X-axis
 *               yColumn:
 *                 type: string
 *                 description: Column name for Y-axis (not used for pie charts)
 *               data:
 *                 type: array
 *                 description: Raw data array for chart generation
 *                 items:
 *                   type: object
 *     responses:
 *       200:
 *         description: Chart configuration generated successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ChartConfiguration'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/chart', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const { analysisId, chartType, xColumn, yColumn, data } = req.body;
    const user = req.user!;
    
    if (!analysisId || !chartType || !xColumn || !data || !Array.isArray(data)) {
      return res.status(400).json({
        error: 'Missing required parameters: analysisId, chartType, xColumn, and data are required',
        code: 'MISSING_PARAMETERS',
        timestamp: new Date().toISOString()
      });
    }
    
    // For pie charts, yColumn is not required
    if (chartType !== 'pie' && !yColumn) {
      return res.status(400).json({
        error: 'yColumn is required for non-pie charts',
        code: 'MISSING_Y_COLUMN',
        timestamp: new Date().toISOString()
      });
    }
    
    const chartConfig = await agentService.generateChart(
      analysisId,
      chartType,
      xColumn,
      yColumn || xColumn, // Use xColumn for pie charts
      data
    );
    
    // Add user context to chart config
    const enhancedChartConfig = {
      ...chartConfig,
      userId: user.id,
      userEmail: user.email,
      createdAt: new Date()
    };
    
    console.log(`Chart generated for user ${user.email}: ${chartType} chart for ${xColumn} vs ${yColumn || xColumn}`);
    
    res.json(enhancedChartConfig);
    
  } catch (error) {
    console.error('Chart generation endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Failed to generate chart',
      code: 'CHART_GENERATION_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/analytics/insights:
 *   post:
 *     summary: Get AI-powered insights from data analysis
 *     tags: [Analytics]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - analysisId
 *               - question
 *             properties:
 *               analysisId:
 *                 type: string
 *                 description: ID of the data analysis
 *               question:
 *                 type: string
 *                 description: Specific question about the data
 *                 example: "What are the main revenue drivers?"
 *               focusArea:
 *                 type: string
 *                 description: Optional focus area for analysis
 *                 enum: [trends, patterns, outliers, correlations, forecasting]
 *     responses:
 *       200:
 *         description: AI-generated insights
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 insights:
 *                   type: array
 *                   items:
 *                     type: string
 *                   description: Array of insight statements
 *                 recommendations:
 *                   type: array
 *                   items:
 *                     type: string
 *                   description: Business recommendations
 *                 confidence:
 *                   type: string
 *                   enum: [high, medium, low]
 *                   description: Confidence level of the analysis
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/insights', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const { analysisId, question, focusArea } = req.body;
    const user = req.user!;
    
    if (!analysisId || !question) {
      return res.status(400).json({
        error: 'Missing required parameters: analysisId and question are required',
        code: 'MISSING_PARAMETERS',
        timestamp: new Date().toISOString()
      });
    }
    
    // Enhanced insights with user context
    const userContext = `${user.accountType === 'BUSINESS' && user.businessName ? user.businessName : `${user.firstName} ${user.lastName}`} (${user.accountType} account)`;
    
    const mockInsights = {
      insights: [
        `Personalized analysis for ${userContext}`,
        'Data analysis feature requires database integration for full implementation',
        'Current analysis capabilities include statistical summaries and basic pattern detection',
        'Chart generation is available for uploaded datasets',
        focusArea ? `Focused analysis on: ${focusArea}` : 'General business intelligence analysis'
      ],
      recommendations: [
        `Recommended for ${user.accountType} accounts: Implement advanced analytics dashboard`,
        'Implement data persistence layer for analysis storage',
        'Add advanced statistical analysis capabilities',
        'Integrate machine learning models for predictive insights'
      ],
      confidence: 'medium' as const,
      userId: user.id,
      userEmail: user.email,
      timestamp: new Date().toISOString()
    };
    
    console.log(`Insights generated for user ${user.email}: ${question}`);
    
    res.json(mockInsights);
    
  } catch (error) {
    console.error('Insights endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Failed to generate insights',
      code: 'INSIGHTS_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/analytics/metrics:
 *   get:
 *     summary: Get system analytics and usage metrics
 *     tags: [Analytics]
 *     security:
 *       - BearerAuth: []
 *     responses:
 *       200:
 *         description: System metrics
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 totalAnalyses:
 *                   type: integer
 *                   description: Total number of data analyses performed
 *                 totalCharts:
 *                   type: integer
 *                   description: Total number of charts generated
 *                 averageProcessingTime:
 *                   type: number
 *                   description: Average processing time in milliseconds
 *                 popularChartTypes:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       type:
 *                         type: string
 *                       count:
 *                         type: integer
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.get('/metrics', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    
    // User-specific metrics
    const metrics = {
      totalAnalyses: 0, // In real implementation, fetch from database
      totalCharts: 0,
      averageProcessingTime: 2500,
      popularChartTypes: [
        { type: 'bar', count: 0 },
        { type: 'line', count: 0 },
        { type: 'pie', count: 0 }
      ],
      userInfo: {
        id: user.id,
        email: user.email,
        accountType: user.accountType,
        memberSince: user.createdAt
      },
      timestamp: new Date().toISOString()
    };
    
    console.log(`Metrics retrieved for user ${user.email}`);
    
    res.json(metrics);
    
  } catch (error) {
    console.error('Metrics endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Failed to retrieve metrics',
      code: 'METRICS_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

export default router;