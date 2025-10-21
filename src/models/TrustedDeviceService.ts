import { PrismaClient } from '@prisma/client';
import crypto from 'crypto';

const prisma = new PrismaClient();

export class TrustedDeviceService {
  /**
   * Generate a device fingerprint from request headers and user agent
   */
  static generateDeviceFingerprint(userAgent: string, ip: string): string {
    const data = `${userAgent}:${ip}`;
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  /**
   * Check if a device is trusted for a user
   */
  static async isDeviceTrusted(userId: string, deviceFingerprint: string): Promise<boolean> {
    try {
      const trustedDevice = await prisma.trustedDevice.findUnique({
        where: {
          userId_deviceFingerprint: {
            userId,
            deviceFingerprint
          }
        }
      });

      if (!trustedDevice || !trustedDevice.isActive) {
        return false;
      }

      // Check if trust period has expired
      if (trustedDevice.trustedUntil < new Date()) {
        // Mark as inactive and return false
        await prisma.trustedDevice.update({
          where: { id: trustedDevice.id },
          data: { isActive: false }
        });
        return false;
      }

      // Update last used timestamp
      await prisma.trustedDevice.update({
        where: { id: trustedDevice.id },
        data: { lastUsed: new Date() }
      });

      return true;
    } catch (error) {
      console.error('Error checking device trust:', error);
      return false;
    }
  }

  /**
   * Add a device to trusted devices list
   */
  static async trustDevice(
    userId: string, 
    deviceFingerprint: string, 
    deviceName?: string,
    trustDays: number = 30
  ): Promise<void> {
    try {
      const trustedUntil = new Date();
      trustedUntil.setDate(trustedUntil.getDate() + trustDays);

      await prisma.trustedDevice.upsert({
        where: {
          userId_deviceFingerprint: {
            userId,
            deviceFingerprint
          }
        },
        update: {
          trustedUntil,
          isActive: true,
          lastUsed: new Date(),
          deviceName
        },
        create: {
          userId,
          deviceFingerprint,
          deviceName,
          trustedUntil,
          isActive: true
        }
      });
    } catch (error) {
      console.error('Error trusting device:', error);
      throw new Error('Failed to trust device');
    }
  }

  /**
   * Remove trust from a device
   */
  static async untrustDevice(userId: string, deviceFingerprint: string): Promise<void> {
    try {
      await prisma.trustedDevice.updateMany({
        where: {
          userId,
          deviceFingerprint
        },
        data: {
          isActive: false
        }
      });
    } catch (error) {
      console.error('Error untrusting device:', error);
      throw new Error('Failed to untrust device');
    }
  }

  /**
   * Get all trusted devices for a user
   */
  static async getUserTrustedDevices(userId: string) {
    try {
      return await prisma.trustedDevice.findMany({
        where: {
          userId,
          isActive: true,
          trustedUntil: {
            gt: new Date()
          }
        },
        select: {
          id: true,
          deviceFingerprint: true,
          deviceName: true,
          trustedUntil: true,
          createdAt: true,
          lastUsed: true
        },
        orderBy: {
          lastUsed: 'desc'
        }
      });
    } catch (error) {
      console.error('Error getting trusted devices:', error);
      throw new Error('Failed to get trusted devices');
    }
  }

  /**
   * Clean up expired trusted devices
   */
  static async cleanupExpiredDevices(): Promise<number> {
    try {
      const result = await prisma.trustedDevice.updateMany({
        where: {
          trustedUntil: {
            lt: new Date()
          },
          isActive: true
        },
        data: {
          isActive: false
        }
      });

      return result.count;
    } catch (error) {
      console.error('Error cleaning up expired devices:', error);
      return 0;
    }
  }

  /**
   * Revoke all trusted devices for a user (security action)
   */
  static async revokeAllUserDevices(userId: string): Promise<number> {
    try {
      const result = await prisma.trustedDevice.updateMany({
        where: {
          userId,
          isActive: true
        },
        data: {
          isActive: false
        }
      });

      return result.count;
    } catch (error) {
      console.error('Error revoking user devices:', error);
      throw new Error('Failed to revoke devices');
    }
  }
}