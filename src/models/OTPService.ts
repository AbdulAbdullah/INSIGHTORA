import { prisma } from '../config/prisma.js';
import type { OTP, OTPType } from '@prisma/client';

export interface CreateOTPData {
  email: string;
  type: OTPType;
}

export class OTPService {
  // Generate a 6-digit OTP code
  static generateCode(): string {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  // Create a new OTP with rate limiting
  static async create(data: CreateOTPData): Promise<{ success: boolean; otp?: OTP; error?: string }> {
    // Check for recent OTP requests (rate limiting)
    const recentOtp = await prisma.oTP.findFirst({
      where: {
        email: data.email,
        type: data.type,
        createdAt: {
          gte: new Date(Date.now() - 60 * 1000), // Within last minute
        },
      },
    });

    if (recentOtp) {
      return { 
        success: false, 
        error: 'Please wait before requesting another OTP. Try again in a minute.' 
      };
    }

    const code = this.generateCode();
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Delete any existing OTPs for this email and type
    await prisma.oTP.deleteMany({
      where: {
        email: data.email,
        type: data.type,
        used: false,
      },
    });

    const otp = await prisma.oTP.create({
      data: {
        email: data.email,
        code,
        type: data.type,
        expiresAt,
      },
    });

    return { success: true, otp };
  }

  // Verify an OTP with attempt tracking
  static async verify(email: string, code: string, type: OTPType): Promise<{ success: boolean; error?: string; attemptsLeft?: number }> {
    const otp = await prisma.oTP.findFirst({
      where: {
        email,
        type,
        used: false,
        expiresAt: {
          gte: new Date(),
        },
      },
    });

    if (!otp) {
      return { success: false, error: 'Invalid or expired OTP' };
    }

    // Check if too many attempts
    if (otp.attempts >= 3) {
      // Mark as used to prevent further attempts
      await prisma.oTP.update({
        where: { id: otp.id },
        data: { used: true },
      });
      return { success: false, error: 'Too many failed attempts. Please request a new OTP.' };
    }

    // Check if code matches
    if (otp.code !== code) {
      // Increment attempts
      const updatedOtp = await prisma.oTP.update({
        where: { id: otp.id },
        data: { attempts: otp.attempts + 1 },
      });
      
      const attemptsLeft = 3 - updatedOtp.attempts;
      return { 
        success: false, 
        error: `Invalid OTP. ${attemptsLeft} attempts remaining.`,
        attemptsLeft 
      };
    }

    // Mark OTP as used - successful verification
    await prisma.oTP.update({
      where: { id: otp.id },
      data: { used: true },
    });

    return { success: true };
  }

  // Clean up expired OTPs
  static async cleanupExpired(): Promise<void> {
    await prisma.oTP.deleteMany({
      where: {
        OR: [
          { expiresAt: { lt: new Date() } },
          { used: true },
        ],
      },
    });
  }

  // Find OTP by email and type
  static async findByEmailAndType(email: string, type: OTPType): Promise<OTP | null> {
    return await prisma.oTP.findFirst({
      where: {
        email,
        type,
        used: false,
        expiresAt: {
          gte: new Date(),
        },
      },
    });
  }
}

export type { OTP, OTPType };