import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class DatabaseManager {
  /**
   * Check if database tables exist and are properly set up
   */
  static async checkDatabaseHealth(): Promise<{ isHealthy: boolean; missingTables: string[]; error?: string }> {
    try {
      const missingTables: string[] = [];
      
      // Check if core tables exist by trying to count records
      try {
        await prisma.user.findFirst();
      } catch (error) {
        if (error instanceof Error && error.message.includes('does not exist')) {
          missingTables.push('users');
        }
      }

      try {
        await prisma.oTP.findFirst();
      } catch (error) {
        if (error instanceof Error && error.message.includes('does not exist')) {
          missingTables.push('otps');
        }
      }

      try {
        await prisma.trustedDevice.findFirst();
      } catch (error) {
        if (error instanceof Error && error.message.includes('does not exist')) {
          missingTables.push('trusted_devices');
        }
      }

      return {
        isHealthy: missingTables.length === 0,
        missingTables
      };

    } catch (error) {
      return {
        isHealthy: false,
        missingTables: [],
        error: error instanceof Error ? error.message : 'Unknown database error'
      };
    }
  }

  /**
   * Apply pending migrations (DEV ONLY - not for production)
   */
  static async applyMigrationsIfNeeded(): Promise<boolean> {
    try {
      // Only run in development
      if (process.env.NODE_ENV === 'production') {
        console.warn('🚫 Auto-migrations disabled in production for safety');
        return false;
      }

      console.log('🔍 Checking for pending migrations...');
      
      // Import exec dynamically to run shell commands
      const { exec } = await import('child_process');
      const { promisify } = await import('util');
      const execAsync = promisify(exec);

      // Run migration command
      const { stdout, stderr } = await execAsync('npx prisma migrate deploy');
      
      if (stderr && !stderr.includes('No pending migrations')) {
        console.error('Migration error:', stderr);
        return false;
      }

      console.log('✅ Database migrations applied successfully');
      return true;

    } catch (error) {
      console.error('Failed to apply migrations:', error);
      return false;
    }
  }

  /**
   * Initialize database - check health and optionally apply migrations
   */
  static async initializeDatabase(): Promise<boolean> {
    try {
      console.log('🔍 Checking database health...');
      
      const health = await this.checkDatabaseHealth();
      
      if (health.isHealthy) {
        console.log('✅ Database is healthy and ready');
        return true;
      }

      if (health.error) {
        console.error('❌ Database connection error:', health.error);
        return false;
      }

      if (health.missingTables.length > 0) {
        console.warn('⚠️  Missing database tables:', health.missingTables.join(', '));
        
        // In development, offer to apply migrations
        if (process.env.NODE_ENV !== 'production') {
          console.log('🔧 Attempting to apply migrations...');
          const migrationSuccess = await this.applyMigrationsIfNeeded();
          
          if (migrationSuccess) {
            // Re-check health after migration
            const newHealth = await this.checkDatabaseHealth();
            if (newHealth.isHealthy) {
              console.log('✅ Database initialized successfully');
              return true;
            }
          }
        }
        
        console.error('❌ Database setup incomplete. Please run: npx prisma migrate dev');
        return false;
      }

      return true;

    } catch (error) {
      console.error('❌ Database initialization failed:', error);
      return false;
    }
  }

  /**
   * Production-safe database check (no auto-migrations)
   */
  static async checkProductionDatabase(): Promise<boolean> {
    console.log('🔍 Performing production database health check...');
    
    const health = await this.checkDatabaseHealth();
    
    if (!health.isHealthy) {
      console.error('❌ PRODUCTION DATABASE ERROR:');
      if (health.error) {
        console.error('   Connection Error:', health.error);
      }
      if (health.missingTables.length > 0) {
        console.error('   Missing Tables:', health.missingTables.join(', '));
        console.error('   ACTION REQUIRED: Apply migrations manually in production');
      }
      return false;
    }
    
    console.log('✅ Production database is healthy');
    return true;
  }
}

export { prisma };
export default DatabaseManager;