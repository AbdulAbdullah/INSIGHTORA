import { Router, Request, Response } from 'express';
import { AuthMiddleware } from '../middleware/auth.js';
import { UserService } from '../models/UserService.js';

const router = Router();

/**
 * @swagger
 * /api/user/profile:
 *   get:
 *     summary: Get user profile information
 *     tags: [User Management]
 *     security:
 *       - BearerAuth: []
 *     responses:
 *       200:
 *         description: User profile retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                 email:
 *                   type: string
 *                 firstName:
 *                   type: string
 *                 lastName:
 *                   type: string
 *                 accountType:
 *                   type: string
 *                   enum: [individual, business]
 *                 businessName:
 *                   type: string
 *                 businessIndustry:
 *                   type: string
 *                 displayName:
 *                   type: string
 *                 createdAt:
 *                   type: string
 *                   format: date-time
 *                 isVerified:
 *                   type: boolean
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.get('/profile', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    
    const userProfile = {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      accountType: user.accountType,
      businessName: user.businessName,
      displayName: user.accountType === 'BUSINESS' && user.businessName
        ? user.businessName
        : `${user.firstName} ${user.lastName}`,
      createdAt: user.createdAt,
      isVerified: user.isVerified
    };

    res.json(userProfile);
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      error: 'Failed to retrieve profile',
      code: 'PROFILE_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/user/profile:
 *   put:
 *     summary: Update user profile information
 *     tags: [User Management]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               firstName:
 *                 type: string
 *               lastName:
 *                 type: string
 *               businessName:
 *                 type: string
 *     responses:
 *       200:
 *         description: Profile updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 user:
 *                   $ref: '#/components/schemas/User'
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.put('/profile', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    const { firstName, lastName, businessName } = req.body;

    // Validate input
    if (firstName !== undefined && (!firstName || firstName.trim().length < 2)) {
      return res.status(400).json({
        error: 'First name must be at least 2 characters long',
        code: 'INVALID_FIRST_NAME',
        timestamp: new Date().toISOString()
      });
    }

    if (lastName !== undefined && (!lastName || lastName.trim().length < 2)) {
      return res.status(400).json({
        error: 'Last name must be at least 2 characters long',
        code: 'INVALID_LAST_NAME',
        timestamp: new Date().toISOString()
      });
    }

    // Update user profile
    const updateData: any = {};
    if (firstName !== undefined) updateData.firstName = firstName.trim();
    if (lastName !== undefined) updateData.lastName = lastName.trim();
    if (businessName !== undefined) updateData.businessName = businessName.trim();

    const updatedUser = await UserService.update(user.id, updateData);

    if (!updatedUser) {
      return res.status(404).json({
        error: 'User not found',
        code: 'USER_NOT_FOUND',
        timestamp: new Date().toISOString()
      });
    }

    // Return updated profile (excluding sensitive data)
    const userProfile = {
      id: updatedUser.id,
      email: updatedUser.email,
      firstName: updatedUser.firstName,
      lastName: updatedUser.lastName,
      accountType: updatedUser.accountType,
      businessName: updatedUser.businessName,
      displayName: updatedUser.accountType === 'BUSINESS' && updatedUser.businessName
        ? updatedUser.businessName
        : `${updatedUser.firstName} ${updatedUser.lastName}`,
      isVerified: updatedUser.isVerified
    };

    res.json({
      message: 'Profile updated successfully',
      user: userProfile
    });

  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      error: 'Failed to update profile',
      code: 'UPDATE_PROFILE_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/user/change-password:
 *   put:
 *     summary: Change user password
 *     tags: [User Management]
 *     security:
 *       - BearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - currentPassword
 *               - newPassword
 *             properties:
 *               currentPassword:
 *                 type: string
 *                 description: Current password
 *               newPassword:
 *                 type: string
 *                 minLength: 6
 *                 description: New password (minimum 6 characters)
 *     responses:
 *       200:
 *         description: Password changed successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.put('/change-password', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;
    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        error: 'Current password and new password are required',
        code: 'MISSING_PASSWORDS',
        timestamp: new Date().toISOString()
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({
        error: 'New password must be at least 6 characters long',
        code: 'INVALID_NEW_PASSWORD',
        timestamp: new Date().toISOString()
      });
    }

    // Verify current password - need to get full user with password
    const fullUser = await UserService.findByEmail(user.email);
    if (!fullUser) {
      return res.status(404).json({
        error: 'User not found',
        code: 'USER_NOT_FOUND',
        timestamp: new Date().toISOString()
      });
    }

    const isCurrentPasswordValid = await UserService.comparePassword(currentPassword, fullUser.password);
    if (!isCurrentPasswordValid) {
      return res.status(400).json({
        error: 'Current password is incorrect',
        code: 'INVALID_CURRENT_PASSWORD',
        timestamp: new Date().toISOString()
      });
    }

    // Update password
    await UserService.changePassword(user.id, newPassword);

    res.json({
      message: 'Password changed successfully'
    });

  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({
      error: 'Failed to change password',
      code: 'CHANGE_PASSWORD_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/user/analytics:
 *   get:
 *     summary: Get user analytics and usage statistics
 *     tags: [User Management]
 *     security:
 *       - BearerAuth: []
 *     responses:
 *       200:
 *         description: User analytics retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 userId:
 *                   type: string
 *                 accountInfo:
 *                   type: object
 *                   properties:
 *                     accountType:
 *                       type: string
 *                     displayName:
 *                       type: string
 *                     memberSince:
 *                       type: string
 *                       format: date-time
 *                 usageStats:
 *                   type: object
 *                   properties:
 *                     totalChatMessages:
 *                       type: number
 *                     totalFileUploads:
 *                       type: number
 *                     totalAnalyses:
 *                       type: number
 *                     lastActivity:
 *                       type: string
 *                       format: date-time
 *       401:
 *         $ref: '#/components/responses/Unauthorized'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.get('/analytics', AuthMiddleware.authenticate, async (req: Request, res: Response) => {
  try {
    const user = req.user!;

    // In a real implementation, these would be calculated from actual usage data
    const analytics = {
      userId: user.id,
      accountInfo: {
        accountType: user.accountType,
        displayName: user.accountType === 'BUSINESS' && user.businessName
          ? user.businessName
          : `${user.firstName} ${user.lastName}`,
        memberSince: user.createdAt,
        isVerified: user.isVerified
      },
      usageStats: {
        totalChatMessages: 0, // Would fetch from chat logs
        totalFileUploads: 0,  // Would fetch from upload logs
        totalAnalyses: 0,     // Would fetch from analysis logs
        lastActivity: new Date() // Would fetch from activity logs
      },
      storageInfo: {
        uploadDirectory: `uploads/${user.id}`,
        tempDirectory: `temp/${user.id}`
      },
      recommendations: user.accountType === 'BUSINESS' 
        ? [
            'Consider uploading quarterly sales data for trend analysis',
            'Set up automated reports for your team',
            'Explore advanced chart types for presentations'
          ]
        : [
            'Try uploading a CSV file to get started with data analysis',
            'Ask questions about your data using the chat feature',
            'Create visualizations to better understand your data'
          ]
    };

    res.json(analytics);
  } catch (error) {
    console.error('User analytics error:', error);
    res.status(500).json({
      error: 'Failed to retrieve analytics',
      code: 'ANALYTICS_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

export default router;