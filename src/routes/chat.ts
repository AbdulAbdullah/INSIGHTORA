import { Router, Request, Response } from 'express';
import { BeeAgentService } from '../BeeAgentService.js';
import { AuthMiddleware } from '../middleware/auth.js';

const router = Router();
const agentService = new BeeAgentService();

/**
 * @swagger
 * /api/chat:
 *   post:
 *     summary: Send a message to the AI assistant
 *     tags: [Chat]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ChatMessage'
 *     responses:
 *       200:
 *         description: Successful response from AI assistant
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ChatResponse'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/chat', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const { message, sessionId } = req.body;
    const user = req.user!; // User is guaranteed to exist due to auth middleware
    
    if (!agentService.validateChatMessage(message)) {
      return res.status(400).json({
        error: 'Invalid message format or length',
        code: 'INVALID_MESSAGE',
        timestamp: new Date().toISOString()
      });
    }
    
    // Enhanced chat with user context
    const response = await agentService.chat(message, undefined, {
      userId: user.id,
      email: user.email,
      accountType: user.accountType,
      displayName: user.accountType === 'BUSINESS' && user.businessName 
        ? user.businessName 
        : `${user.firstName} ${user.lastName}`
    });
    
    res.json({
      response,
      sessionId: sessionId || user.id,
      user: {
        id: user.id,
        displayName: user.accountType === 'BUSINESS' && user.businessName 
          ? user.businessName 
          : `${user.firstName} ${user.lastName}`,
        accountType: user.accountType
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Chat endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Internal server error',
      code: 'CHAT_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/chat/data:
 *   post:
 *     summary: Chat with AI assistant about specific data analysis
 *     tags: [Chat]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - message
 *               - analysisId
 *             properties:
 *               message:
 *                 type: string
 *                 description: Question about the data
 *                 example: "What are the key trends in this dataset?"
 *               analysisId:
 *                 type: string
 *                 description: ID of the data analysis to reference
 *               sessionId:
 *                 type: string
 *                 description: Optional session identifier
 *     responses:
 *       200:
 *         description: AI response about the data
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ChatResponse'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       404:
 *         description: Analysis not found
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/chat/data', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const { message, analysisId, sessionId } = req.body;
    
    if (!agentService.validateChatMessage(message) || !analysisId) {
      return res.status(400).json({
        error: 'Invalid message or missing analysis ID',
        code: 'INVALID_REQUEST',
        timestamp: new Date().toISOString()
      });
    }
    
    // In a real implementation, you would retrieve the analysis from a database
    // For now, return an error indicating the feature needs data storage
    return res.status(404).json({
      error: 'Data context feature requires database implementation',
      code: 'FEATURE_NOT_IMPLEMENTED',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Data chat endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Internal server error',
      code: 'DATA_CHAT_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/chat/clear:
 *   post:
 *     summary: Clear chat memory and start fresh conversation
 *     tags: [Chat]
 *     security:
 *       - BearerAuth: []
 *     responses:
 *       200:
 *         description: Memory cleared successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                   example: "Chat memory cleared successfully"
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/clear', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    await agentService.clearMemory();
    
    res.json({
      message: 'Chat memory cleared successfully',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Clear memory endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Failed to clear memory',
      code: 'CLEAR_MEMORY_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

export default router;