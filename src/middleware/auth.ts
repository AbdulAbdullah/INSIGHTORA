import { Request, Response, NextFunction } from 'express';
import jwt, { SignOptions } from 'jsonwebtoken';
import { UserService, UserWithoutPassword } from '../models/UserService.js';
import { connectToDatabase } from '../config/prisma.js';

// Extend Request interface to include user
declare global {
  namespace Express {
    interface Request {
      user?: UserWithoutPassword;
    }
  }
}

interface JWTPayload {
  userId: string;
  email: string;
  iat?: number;
  exp?: number;
}

interface LoginSessionPayload {
  userId: string;
  deviceFingerprint: string;
  iat?: number;
  exp?: number;
}

export class AuthMiddleware {
  // Generate access and refresh tokens
  static generateTokens(user: UserWithoutPassword): { accessToken: string; refreshToken: string } {
    const payload: JWTPayload = {
      userId: user.id,
      email: user.email
    };

    const accessTokenOptions: SignOptions = {
      expiresIn: (process.env.JWT_EXPIRES_IN || '1h') as string,
      issuer: 'bee-agent-framework',
      audience: 'bee-agent-users'
    } as SignOptions;

    const refreshTokenOptions: SignOptions = {
      expiresIn: (process.env.JWT_REFRESH_EXPIRES_IN || '7d') as string,
      issuer: 'bee-agent-framework',
      audience: 'bee-agent-users'
    } as SignOptions;

    const accessToken = jwt.sign(payload, process.env.JWT_SECRET!, accessTokenOptions);
    const refreshToken = jwt.sign(payload, process.env.JWT_REFRESH_SECRET!, refreshTokenOptions);

    return { accessToken, refreshToken };
  }

  // Generate login session token (temporary, expires in 10 minutes)
  static generateLoginSessionToken(userId: string, deviceFingerprint: string): string {
    const payload: LoginSessionPayload = {
      userId,
      deviceFingerprint
    };

    const options: SignOptions = {
      expiresIn: '10m', // 10 minutes for OTP verification
      issuer: 'bee-agent-framework',
      audience: 'bee-agent-login'
    } as SignOptions;

    return jwt.sign(payload, process.env.JWT_SECRET!, options);
  }

  // Verify login session token
  static verifyLoginSessionToken(token: string): LoginSessionPayload | null {
    try {
      if (!process.env.JWT_SECRET) {
        throw new Error('JWT_SECRET not configured');
      }
      const decoded = jwt.verify(token, process.env.JWT_SECRET) as LoginSessionPayload;
      return decoded;
    } catch (error) {
      console.error('Login session token verification failed:', error);
      return null;
    }
  }

  // Verify token
  static verifyToken(token: string, secret: string): JWTPayload | null {
    try {
      const decoded = jwt.verify(token, secret) as JWTPayload;
      return decoded;
    } catch (error) {
      console.error('Token verification failed:', error);
      return null;
    }
  }

  // Authentication middleware
  static authenticate = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // Check if database is connected
      const isDatabaseConnected = await connectToDatabase();
      if (!isDatabaseConnected) {
        res.status(503).json({
          error: 'Authentication service unavailable. Database connection required.',
          code: 'SERVICE_UNAVAILABLE',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        res.status(401).json({
          error: 'Access token required. Please provide a valid Bearer token.',
          code: 'NO_TOKEN',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const token = authHeader.substring(7); // Remove 'Bearer ' prefix
      
      if (!process.env.JWT_SECRET) {
        console.error('JWT_SECRET not configured');
        res.status(500).json({
          error: 'Authentication configuration error',
          code: 'AUTH_CONFIG_ERROR',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const decoded = AuthMiddleware.verifyToken(token, process.env.JWT_SECRET);
      
      if (!decoded) {
        res.status(401).json({
          error: 'Invalid or expired token. Please login again.',
          code: 'INVALID_TOKEN',
          timestamp: new Date().toISOString()
        });
        return;
      }

      // Get user from database
      const user = await UserService.findById(decoded.userId);
      
      if (!user) {
        res.status(401).json({
          error: 'User not found. Token may be invalid.',
          code: 'USER_NOT_FOUND',
          timestamp: new Date().toISOString()
        });
        return;
      }

      if (!user.isActive) {
        res.status(401).json({
          error: 'Account is deactivated. Please contact support.',
          code: 'ACCOUNT_DEACTIVATED',
          timestamp: new Date().toISOString()
        });
        return;
      }

      // Attach user to request
      req.user = user;
      next();

    } catch (error) {
      console.error('Authentication middleware error:', error);
      res.status(500).json({
        error: 'Authentication service error',
        code: 'AUTH_SERVICE_ERROR',
        timestamp: new Date().toISOString()
      });
    }
  };

  // Optional authentication middleware (doesn't fail if no token)
  static optionalAuthenticate = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        // No token provided, continue without user
        next();
        return;
      }

      const token = authHeader.substring(7);
      
      if (!process.env.JWT_SECRET) {
        next();
        return;
      }

      const decoded = AuthMiddleware.verifyToken(token, process.env.JWT_SECRET);
      
      if (decoded) {
        const user = await UserService.findById(decoded.userId);
        if (user && user.isActive) {
          req.user = user;
        }
      }

      next();

    } catch (error) {
      console.error('Optional authentication error:', error);
      // Continue without user on error
      next();
    }
  };

  // Refresh token middleware
  static refreshToken = async (req: Request, res: Response): Promise<void> => {
    try {
      const { refreshToken } = req.body;
      
      if (!refreshToken) {
        res.status(400).json({
          error: 'Refresh token is required',
          code: 'NO_REFRESH_TOKEN',
          timestamp: new Date().toISOString()
        });
        return;
      }

      if (!process.env.JWT_REFRESH_SECRET) {
        res.status(500).json({
          error: 'Token configuration error',
          code: 'TOKEN_CONFIG_ERROR',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const decoded = AuthMiddleware.verifyToken(refreshToken, process.env.JWT_REFRESH_SECRET);
      
      if (!decoded) {
        res.status(401).json({
          error: 'Invalid refresh token',
          code: 'INVALID_REFRESH_TOKEN',
          timestamp: new Date().toISOString()
        });
        return;
      }

      const user = await UserService.findById(decoded.userId);
      
      if (!user || !user.isActive) {
        res.status(401).json({
          error: 'User not found or inactive',
          code: 'USER_INVALID',
          timestamp: new Date().toISOString()
        });
        return;
      }

      // Generate new tokens
      const tokens = AuthMiddleware.generateTokens(user);
      
      res.json({
        message: 'Tokens refreshed successfully',
        ...tokens,
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          accountType: user.accountType
        }
      });

    } catch (error) {
      console.error('Token refresh error:', error);
      res.status(500).json({
        error: 'Token refresh failed',
        code: 'REFRESH_ERROR',
        timestamp: new Date().toISOString()
      });
    }
  };
}

export default AuthMiddleware;