import { Router, Request, Response } from 'express';
import { UserService, CreateUserData } from '../models/UserService.js';
import { OTPService, CreateOTPData } from '../models/OTPService.js';
import { TrustedDeviceService } from '../models/TrustedDeviceService.js';
import { emailService } from '../services/EmailService.js';
import { AuthMiddleware } from '../middleware/auth.js';
import { connectToDatabase } from '../config/prisma.js';
import { AccountType, OTPType } from '@prisma/client';

const router = Router();

/**
 * @swagger
 * /api/auth/register:
 *   post:
 *     summary: Register a new user account
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - password
 *               - firstName
 *               - lastName
 *               - accountType
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *                 example: "user@example.com"
 *               password:
 *                 type: string
 *                 minLength: 8
 *                 example: "SecurePass123"
 *               firstName:
 *                 type: string
 *                 minLength: 2
 *                 example: "John"
 *               lastName:
 *                 type: string
 *                 minLength: 2
 *                 example: "Doe"
 *               accountType:
 *                 type: string
 *                 enum: [individual, business]
 *                 example: "individual"
 *               businessName:
 *                 type: string
 *                 description: "Required for business accounts"
 *                 example: "Acme Corporation"
 *     responses:
 *       201:
 *         description: User registered successfully, OTP sent
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 userId:
 *                   type: string
 *                 email:
 *                   type: string
 *                 otpSent:
 *                   type: boolean
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       409:
 *         description: Email already exists
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/register', async (req: Request, res: Response) => {
  try {
    // Check database connection
    const isConnected = await connectToDatabase();
    if (!isConnected) {
      return res.status(503).json({
        error: 'Registration service unavailable. Please try again later.',
        code: 'SERVICE_UNAVAILABLE',
        timestamp: new Date().toISOString()
      });
    }

    const { email, password, firstName, lastName, accountType, businessName } = req.body;

    // Validation
    if (!email || !password || !firstName || !lastName || !accountType) {
      return res.status(400).json({
        error: 'All required fields must be provided',
        code: 'MISSING_FIELDS',
        timestamp: new Date().toISOString()
      });
    }

    if (password.length < 8) {
      return res.status(400).json({
        error: 'Password must be at least 8 characters long',
        code: 'INVALID_PASSWORD',
        timestamp: new Date().toISOString()
      });
    }

    if (accountType === 'business' && !businessName) {
      return res.status(400).json({
        error: 'Business name is required for business accounts',
        code: 'MISSING_BUSINESS_NAME',
        timestamp: new Date().toISOString()
      });
    }

    // Check if user already exists
    const existingUser = await UserService.findByEmail(email);
    if (existingUser) {
      return res.status(409).json({
        error: 'An account with this email already exists',
        code: 'EMAIL_EXISTS',
        timestamp: new Date().toISOString()
      });
    }

    // Create user
    const userData: CreateUserData = {
      email: email.toLowerCase().trim(),
      password,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      accountType: accountType.toUpperCase() as AccountType,
      businessName: businessName?.trim()
    };

    const user = await UserService.create(userData);

    // Generate and send OTP
    const otpResult = await OTPService.create({
      email: user.email,
      type: OTPType.EMAIL_VERIFICATION
    });

    if (!otpResult.success) {
      return res.status(429).json({
        error: otpResult.error,
        code: 'OTP_RATE_LIMITED',
        timestamp: new Date().toISOString()
      });
    }

    // Send verification email
    const emailSent = await emailService.sendOTPEmail(
      user.email,
      otpResult.otp!.code,
      user.firstName,
      'registration'
    );

    console.log(`User registered: ${user.email} (${user.accountType})`);
    console.log(`OTP sent: ${emailSent ? 'Success' : 'Failed'}`);

    res.status(201).json({
      message: 'Registration successful. Please check your email for verification code.',
      userId: user.id,
      email: user.email,
      otpSent: emailSent
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      error: 'Registration failed. Please try again.',
      code: 'REGISTRATION_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/auth/verify-email:
 *   post:
 *     summary: Verify email address with OTP
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - otp
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *               otp:
 *                 type: string
 *                 pattern: '^[0-9]{6}$'
 *                 example: "123456"
 *     responses:
 *       200:
 *         description: Email verified successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 user:
 *                   $ref: '#/components/schemas/User'
 *                 nextStep:
 *                   type: string
 *                   description: Instructions for next step (login)
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       401:
 *         description: Invalid or expired OTP
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/verify-email', async (req: Request, res: Response) => {
  try {
    const { email, otp } = req.body;

    if (!email || !otp) {
      return res.status(400).json({
        error: 'Email and OTP are required',
        code: 'MISSING_FIELDS',
        timestamp: new Date().toISOString()
      });
    }

    // Verify OTP
    const otpResult = await OTPService.verify(
      email.toLowerCase().trim(),
      otp.trim(),
      OTPType.EMAIL_VERIFICATION
    );

    if (!otpResult.success) {
      return res.status(401).json({
        error: otpResult.error,
        code: 'INVALID_OTP',
        attemptsLeft: otpResult.attemptsLeft,
        timestamp: new Date().toISOString()
      });
    }

    // Mark user as verified
    const user = await UserService.verifyEmail(email.toLowerCase().trim());
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        code: 'USER_NOT_FOUND',
        timestamp: new Date().toISOString()
      });
    }

    // Send welcome email
    const welcomeEmailSent = await emailService.sendWelcomeEmail(
      user.email,
      user.firstName,
      user.accountType.toLowerCase(),
      user.accountType === AccountType.BUSINESS && user.businessName
        ? user.businessName
        : `${user.firstName} ${user.lastName}`
    );

    console.log(`Email verified: ${user.email}`);
    console.log(`Welcome email sent: ${welcomeEmailSent ? 'Success' : 'Failed'}`);

    res.json({
      message: 'Email verified successfully! Please login to access your BI Assistant.',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        accountType: user.accountType,
        businessName: user.businessName,
        isVerified: user.isVerified
      },
      nextStep: 'Please proceed to login with your credentials to receive access tokens.'
    });

  } catch (error) {
    console.error('Email verification error:', error);
    res.status(500).json({
      error: 'Email verification failed',
      code: 'VERIFICATION_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: Login with email and password (Step 1 - sends login OTP)
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - password
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *               password:
 *                 type: string
 *               deviceFingerprint:
 *                 type: string
 *                 description: Optional device identifier for trusted device check
 *     responses:
 *       200:
 *         description: Credentials valid, login OTP sent (or login successful if device trusted)
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 requiresOTP:
 *                   type: boolean
 *                 maskedEmail:
 *                   type: string
 *                 otpSent:
 *                   type: boolean
 *                 user:
 *                   $ref: '#/components/schemas/User'
 *                   description: Only returned if device is trusted (no OTP required)
 *                 accessToken:
 *                   type: string
 *                   description: Only returned if device is trusted (no OTP required)
 *                 refreshToken:
 *                   type: string
 *                   description: Only returned if device is trusted (no OTP required)
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       401:
 *         description: Invalid credentials or unverified email
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { email, password, deviceFingerprint } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        error: 'Email and password are required',
        code: 'MISSING_CREDENTIALS',
        timestamp: new Date().toISOString()
      });
    }

    // Find user
    const user = await UserService.findByEmail(email.toLowerCase().trim());
    if (!user) {
      return res.status(401).json({
        error: 'Invalid email or password',
        code: 'INVALID_CREDENTIALS',
        timestamp: new Date().toISOString()
      });
    }

    // Check password
    const isValidPassword = await UserService.comparePassword(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({
        error: 'Invalid email or password',
        code: 'INVALID_CREDENTIALS',
        timestamp: new Date().toISOString()
      });
    }

    // Check if email is verified
    if (!user.isVerified) {
      return res.status(401).json({
        error: 'Please verify your email address before logging in',
        code: 'EMAIL_NOT_VERIFIED',
        timestamp: new Date().toISOString()
      });
    }

    // Check if account is active
    if (!user.isActive) {
      return res.status(401).json({
        error: 'Account is deactivated. Please contact support.',
        code: 'ACCOUNT_DEACTIVATED',
        timestamp: new Date().toISOString()
      });
    }

    // Generate device fingerprint if not provided
    const userAgent = req.headers['user-agent'] || '';
    const clientIP = req.ip || req.connection.remoteAddress || '';
    const finalDeviceFingerprint = deviceFingerprint || 
      TrustedDeviceService.generateDeviceFingerprint(userAgent, clientIP);

    // Check if device is trusted (and user is not business account)
    const shouldSkipOTP = user.accountType === AccountType.INDIVIDUAL && 
      await TrustedDeviceService.isDeviceTrusted(user.id, finalDeviceFingerprint);

    if (shouldSkipOTP) {
      // Device is trusted, complete login
      await UserService.updateLastLogin(user.id);
      
      // Get user without password for token generation
      const userForToken = await UserService.findById(user.id);
      if (!userForToken) {
        return res.status(500).json({
          error: 'User data error',
          code: 'USER_DATA_ERROR',
          timestamp: new Date().toISOString()
        });
      }
      
      const tokens = AuthMiddleware.generateTokens(userForToken);

      console.log(`User logged in (trusted device): ${user.email}`);

      return res.json({
        message: 'Login successful',
        requiresOTP: false,
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName,
          accountType: user.accountType,
          businessName: user.businessName,
          isVerified: user.isVerified
        },
        ...tokens
      });
    }

    // Generate and send login OTP
    const otpResult = await OTPService.create({
      email: user.email,
      type: OTPType.LOGIN_VERIFICATION
    });

    if (!otpResult.success) {
      return res.status(429).json({
        error: otpResult.error,
        code: 'OTP_RATE_LIMITED',
        timestamp: new Date().toISOString()
      });
    }

    // Send login OTP email
    const emailSent = await emailService.sendOTPEmail(
      user.email,
      otpResult.otp!.code,
      user.firstName,
      'login'
    );

    console.log(`Login OTP sent: ${user.email} (Email sent: ${emailSent ? 'Success' : 'Failed'})`);

    res.json({
      message: 'Login OTP sent to your email. Please verify to complete login.',
      requiresOTP: true,
      maskedEmail: user.email.replace(/(.{2})(.*)(@.*)/, '$1***$3'),
      otpSent: emailSent
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      error: 'Login failed',
      code: 'LOGIN_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/auth/verify-login:
 *   post:
 *     summary: Verify login OTP and complete authentication (FINAL TOKEN ISSUANCE)
 *     description: This is the ONLY endpoint that issues access/refresh tokens after full 2FA verification
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - otp
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *                 description: User's email address
 *               otp:
 *                 type: string
 *                 pattern: '^[0-9]{6}$'
 *                 example: "123456"
 *                 description: 6-digit OTP received via email
 *               trustDevice:
 *                 type: boolean
 *                 description: Whether to trust this device for future logins
 *                 default: false
 *               deviceName:
 *                 type: string
 *                 description: Optional name for the trusted device
 *     responses:
 *       200:
 *         description: Login completed successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 user:
 *                   $ref: '#/components/schemas/User'
 *                 accessToken:
 *                   type: string
 *                 refreshToken:
 *                   type: string
 *                 deviceTrusted:
 *                   type: boolean
 *       400:
 *         $ref: '#/components/responses/BadRequest'
 *       401:
 *         description: Invalid OTP or login session
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/verify-login', async (req: Request, res: Response) => {
  try {
    const { email, otp, trustDevice = false, deviceName } = req.body;

    if (!email || !otp) {
      return res.status(400).json({
        error: 'Email and OTP are required',
        code: 'MISSING_FIELDS',
        timestamp: new Date().toISOString()
      });
    }

    // Get user by email
    const user = await UserService.findByEmail(email.toLowerCase().trim());
    if (!user) {
      return res.status(401).json({
        error: 'Invalid email or OTP',
        code: 'INVALID_CREDENTIALS',
        timestamp: new Date().toISOString()
      });
    }

    // Check if user is verified and active
    if (!user.isVerified) {
      return res.status(401).json({
        error: 'Please verify your email address first',
        code: 'EMAIL_NOT_VERIFIED',
        timestamp: new Date().toISOString()
      });
    }

    if (!user.isActive) {
      return res.status(401).json({
        error: 'Account is deactivated',
        code: 'ACCOUNT_DEACTIVATED',
        timestamp: new Date().toISOString()
      });
    }

    // Verify login OTP
    const otpResult = await OTPService.verify(
      user.email,
      otp.trim(),
      OTPType.LOGIN_VERIFICATION
    );

    if (!otpResult.success) {
      return res.status(401).json({
        error: otpResult.error,
        code: 'INVALID_OTP',
        attemptsLeft: otpResult.attemptsLeft,
        timestamp: new Date().toISOString()
      });
    }

    // Update last login
    await UserService.updateLastLogin(user.id);

    // Trust device if requested (and account type allows it)
    let deviceTrusted = false;
    if (trustDevice && user.accountType === AccountType.INDIVIDUAL) {
      try {
        const userAgent = req.headers['user-agent'] || '';
        const clientIP = req.ip || req.connection.remoteAddress || '';
        const deviceFingerprint = TrustedDeviceService.generateDeviceFingerprint(userAgent, clientIP);
        
        await TrustedDeviceService.trustDevice(
          user.id,
          deviceFingerprint,
          deviceName
        );
        deviceTrusted = true;
        console.log(`Device trusted for user: ${user.email}`);
      } catch (error) {
        console.error('Failed to trust device:', error);
        // Don't fail the login if device trust fails
      }
    }

    // Generate final authentication tokens
    const userForToken = await UserService.findById(user.id);
    if (!userForToken) {
      return res.status(500).json({
        error: 'User data error',
        code: 'USER_DATA_ERROR',
        timestamp: new Date().toISOString()
      });
    }
    
    const tokens = AuthMiddleware.generateTokens(userForToken);

    console.log(`User login completed: ${user.email} (Device trusted: ${deviceTrusted})`);

    res.json({
      message: 'Login completed successfully',
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        accountType: user.accountType,
        businessName: user.businessName,
        isVerified: user.isVerified
      },
      deviceTrusted,
      ...tokens
    });

  } catch (error) {
    console.error('Login verification error:', error);
    res.status(500).json({
      error: 'Login verification failed',
      code: 'LOGIN_VERIFICATION_ERROR',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * @swagger
 * /api/auth/refresh:
 *   post:
 *     summary: Refresh access token using refresh token
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - refreshToken
 *             properties:
 *               refreshToken:
 *                 type: string
 *     responses:
 *       200:
 *         description: Tokens refreshed successfully
 *       401:
 *         description: Invalid refresh token
 *       500:
 *         $ref: '#/components/responses/InternalError'
 */
router.post('/refresh', AuthMiddleware.refreshToken);

export default router;