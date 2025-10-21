import { PrismaClient } from '@prisma/client';

// Global instance to prevent multiple connections in development
declare global {
  var __prisma: PrismaClient | undefined;
}

// Create Prisma client instance
export const prisma = globalThis.__prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'warn', 'error'] : ['error'],
});

// In development, store the client globally to prevent multiple instances
if (process.env.NODE_ENV === 'development') {
  globalThis.__prisma = prisma;
}

// Database connection helper
export async function connectToDatabase(): Promise<boolean> {
  try {
    console.log('Connecting to PostgreSQL...');
    
    // Test the connection
    await prisma.$connect();
    console.log('PostgreSQL connected successfully!');
    return true;
    
  } catch (error) {
    console.error('PostgreSQL connection error:', error);
    console.log('Database connection failed, running without database features');
    return false;
  }
}

// Graceful shutdown
export async function disconnectFromDatabase(): Promise<void> {
  try {
    await prisma.$disconnect();
    console.log('PostgreSQL disconnected successfully');
  } catch (error) {
    console.error('Error disconnecting from PostgreSQL:', error);
  }
}

// Health check
export async function isDatabaseConnected(): Promise<boolean> {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return true;
  } catch {
    return false;
  }
}

export default prisma;