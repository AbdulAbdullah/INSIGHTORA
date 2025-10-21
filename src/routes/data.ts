import { Router, Request, Response } from 'express';
import multer from 'multer';
import { BeeAgentService } from '../BeeAgentService.js';
import { AuthMiddleware } from '../middleware/auth.js';
import * as fs from 'fs/promises';
import * as path from 'path';

const router = Router();
const agentService = new BeeAgentService();

// Configure multer for file uploads with user-specific storage
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const user = (req as any).user;
    const userUploadDir = path.join(process.cwd(), 'uploads', user ? user.id : 'anonymous');
    try {
      await fs.mkdir(userUploadDir, { recursive: true });
      cb(null, userUploadDir);
    } catch (error) {
      cb(error, userUploadDir);
    }
  },
  filename: (req, file, cb) => {
    // Generate unique filename with timestamp and user info
    const user = (req as any).user;
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const extension = path.extname(file.originalname);
    const userPrefix = user ? `${user.id}-` : '';
    cb(null, `${userPrefix}${file.fieldname}-${uniqueSuffix}${extension}`);
  }
});

// File filter for security
const fileFilter = (req: any, file: Express.Multer.File, cb: any) => {
  const allowedMimes = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];
  
  const allowedExtensions = ['.csv', '.xls', '.xlsx'];
  const fileExtension = path.extname(file.originalname).toLowerCase();
  
  if (allowedMimes.includes(file.mimetype) || allowedExtensions.includes(fileExtension)) {
    cb(null, true);
  } else {
    cb(new Error('Invalid file type. Only CSV and Excel files are allowed.'), false);
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
    files: 1
  }
});

/**
 * @swagger
 * /api/data/upload:
 *   post:
 *     summary: Upload and analyze a CSV or Excel file
 *     tags: [Data Upload]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               file:
 *                 type: string
 *                 format: binary
 *                 description: CSV or Excel file to analyze
 *     responses:
 *       200:
 *         description: File uploaded and analyzed successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/DataAnalysis'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       413:
 *         description: File too large
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/upload', AuthMiddleware.authenticate, upload.single('file'), async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    
    if (!req.file) {
      return res.status(400).json({
        error: 'No file uploaded',
        code: 'NO_FILE',
        timestamp: new Date().toISOString()
      });
    }
    
    const filePath = req.file.path;
    const fileName = req.file.originalname;
    
    console.log(`Processing uploaded file for user ${user.email}: ${fileName}`);
    
    // Analyze the CSV file with user context
    const analysisResult = await agentService.analyzeCSVFile(filePath, fileName);
    
    // Add user context to analysis result
    const enhancedResult = {
      ...analysisResult,
      userId: user.id,
      userEmail: user.email,
      uploadedAt: new Date()
    };
    
    // Keep file for user's future reference (don't delete immediately)
    console.log(`Analysis completed for user ${user.email}: ${fileName} - ${analysisResult.rowCount} rows, ${analysisResult.columns.length} columns`);
    
    res.json(enhancedResult);
    
  } catch (error) {
    console.error('File upload endpoint error:', error);
    
    // Clean up file if it exists and there was an error
    if (req.file?.path) {
      try {
        // Only cleanup on error, keep successful uploads for user
        await fs.unlink(req.file.path);
      } catch (cleanupError) {
        console.warn('Failed to cleanup file after error:', cleanupError);
      }
    }
    
    res.status(500).json({
      error: error.message || 'Failed to process uploaded file',
      code: 'UPLOAD_PROCESSING_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/data/sample:
 *   get:
 *     summary: Get sample data for testing the analysis features
 *     tags: [Data Upload]
 *     security:
 *       - BearerAuth: []
 *     responses:
 *       200:
 *         description: Sample data analysis result
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/DataAnalysis'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.get('/sample', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    
    // Generate sample data for demonstration
    const sampleData = [
      { product: 'Laptop', category: 'Electronics', sales: 1200, quarter: 'Q1' },
      { product: 'Phone', category: 'Electronics', sales: 800, quarter: 'Q1' },
      { product: 'Desk', category: 'Furniture', sales: 300, quarter: 'Q1' },
      { product: 'Chair', category: 'Furniture', sales: 150, quarter: 'Q1' },
      { product: 'Laptop', category: 'Electronics', sales: 1350, quarter: 'Q2' },
      { product: 'Phone', category: 'Electronics', sales: 900, quarter: 'Q2' },
      { product: 'Desk', category: 'Furniture', sales: 320, quarter: 'Q2' },
      { product: 'Chair', category: 'Furniture', sales: 180, quarter: 'Q2' }
    ];
    
    // Create a temporary CSV file in user's directory
    const userTempDir = path.join(process.cwd(), 'temp', user.id);
    await fs.mkdir(userTempDir, { recursive: true });
    
    const csvContent = [
      'product,category,sales,quarter',
      ...sampleData.map(row => `${row.product},${row.category},${row.sales},${row.quarter}`)
    ].join('\n');
    
    const tempFilePath = path.join(userTempDir, 'sample-data.csv');
    await fs.writeFile(tempFilePath, csvContent);
    
    // Analyze the sample data
    const analysisResult = await agentService.analyzeCSVFile(tempFilePath, 'sample-sales-data.csv');
    
    // Add user context
    const enhancedResult = {
      ...analysisResult,
      userId: user.id,
      userEmail: user.email,
      isSampleData: true,
      uploadedAt: new Date()
    };
    
    // Clean up temp file
    try {
      await fs.unlink(tempFilePath);
    } catch (cleanupError) {
      console.warn('Failed to cleanup temp file:', cleanupError);
    }
    
    res.json(enhancedResult);
    
  } catch (error) {
    console.error('Sample data endpoint error:', error);
    res.status(500).json({
      error: error.message || 'Failed to generate sample data',
      code: 'SAMPLE_DATA_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

export default router;