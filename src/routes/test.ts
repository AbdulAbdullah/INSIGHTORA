import { Router, Request, Response } from 'express';

const router = Router();

// Test endpoints that work without database
/**
 * @swagger
 * /api/test/auth:
 *   post:
 *     summary: Test authentication without database
 *     tags: [Testing]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *               password:
 *                 type: string
 *     responses:
 *       200:
 *         description: Test authentication successful
 */
router.post('/auth', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;
    
    // Mock authentication for testing
    if (email && password) {
      const mockToken = 'test-jwt-token-' + Date.now();
      
      res.json({
        message: 'Test authentication successful',
        user: {
          id: 'test-user-123',
          email: email,
          firstName: 'Test',
          lastName: 'User',
          accountType: 'individual'
        },
        token: mockToken,
        note: 'This is a test response without database connection'
      });
    } else {
      res.status(400).json({
        error: 'Email and password required',
        timestamp: new Date().toISOString()
      });
    }
  } catch (error) {
    res.status(500).json({
      error: 'Test authentication failed',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/test/chat:
 *   post:
 *     summary: Test chat without authentication
 *     tags: [Testing]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               message:
 *                 type: string
 *     responses:
 *       200:
 *         description: Test chat response
 */
router.post('/chat', async (req: Request, res: Response) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({
        error: 'Message is required',
        timestamp: new Date().toISOString()
      });
    }
    
    // Mock AI response
    const responses = [
      'This is a test response from the BI Assistant.',
      'I can help you analyze data and generate insights.',
      'Try uploading a CSV file to see data analysis features.',
      'The authentication system is ready once you connect to MongoDB.'
    ];
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    res.json({
      response: `${randomResponse} You asked: "${message}"`,
      timestamp: new Date().toISOString(),
      note: 'This is a test response without AI integration'
    });
    
  } catch (error) {
    res.status(500).json({
      error: 'Test chat failed',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/test/status:
 *   get:
 *     summary: Check system status
 *     tags: [Testing]
 *     responses:
 *       200:
 *         description: System status
 */
router.get('/status', async (req: Request, res: Response) => {
  res.json({
    status: 'System running',
    timestamp: new Date().toISOString(),
    features: {
      server: 'Running',
      groqAI: process.env.GROQ_API_KEY ? 'Configured' : 'Not configured',
      mongodb: 'Disconnected (test mode)',
      authentication: 'Ready (needs MongoDB)',
      email: process.env.EMAIL_USER ? 'Configured' : 'Not configured'
    },
    endpoints: {
      '/api/test/auth': 'Test authentication',
      '/api/test/chat': 'Test chat',
      '/api/test/status': 'System status',
      '/api-docs': 'API documentation'
    }
  });
});

export default router;