import { prisma } from '../config/prisma.js';
import bcrypt from 'bcryptjs';
import type { User, AccountType } from '@prisma/client';

export interface CreateUserData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  accountType: AccountType;
  businessName?: string;
}

export interface UserWithoutPassword extends Omit<User, 'password'> {}

export class UserService {
  // Create a new user
  static async create(userData: CreateUserData): Promise<UserWithoutPassword> {
    const hashedPassword = await bcrypt.hash(userData.password, 12);
    
    const user = await prisma.user.create({
      data: {
        ...userData,
        password: hashedPassword,
      },
    });

    // Return user without password
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  // Find user by email
  static async findByEmail(email: string): Promise<User | null> {
    return await prisma.user.findUnique({
      where: { email },
    });
  }

  // Find user by ID
  static async findById(id: string): Promise<UserWithoutPassword | null> {
    const user = await prisma.user.findUnique({
      where: { id },
    });

    if (!user) return null;

    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  // Update user
  static async update(id: string, data: Partial<User>): Promise<UserWithoutPassword | null> {
    const user = await prisma.user.update({
      where: { id },
      data,
    });

    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  // Verify user email
  static async verifyEmail(email: string): Promise<UserWithoutPassword | null> {
    const user = await prisma.user.update({
      where: { email },
      data: { isVerified: true },
    });

    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  // Update last login
  static async updateLastLogin(id: string): Promise<void> {
    await prisma.user.update({
      where: { id },
      data: { lastLogin: new Date() },
    });
  }

  // Compare password
  static async comparePassword(plainPassword: string, hashedPassword: string): Promise<boolean> {
    return await bcrypt.compare(plainPassword, hashedPassword);
  }

  // Change password
  static async changePassword(id: string, newPassword: string): Promise<void> {
    const hashedPassword = await bcrypt.hash(newPassword, 12);
    await prisma.user.update({
      where: { id },
      data: { password: hashedPassword },
    });
  }

  // Check if email exists
  static async emailExists(email: string): Promise<boolean> {
    const user = await prisma.user.findUnique({
      where: { email },
    });
    return !!user;
  }
}

export type { User, AccountType };