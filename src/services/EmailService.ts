import nodemailer from 'nodemailer';

export interface EmailConfig {
  host: string;
  port: number;
  secure: boolean;
  user: string;
  password: string;
  fromEmail: string;
  fromName: string;
}

export class EmailService {
  private transporter: nodemailer.Transporter;
  private config: EmailConfig;

  constructor() {
    this.config = {
      host: process.env.EMAIL_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '587'),
      secure: process.env.EMAIL_SECURE === 'true',
      user: process.env.EMAIL_HOST_USER || '',
      password: process.env.EMAIL_HOST_PASSWORD || '',
      fromEmail: process.env.DEFAULT_FROM_EMAIL || 'noreply@notarize.com',
      fromName: process.env.DEFAULT_FROM_NAME || 'RON API Service'
    };

    this.validateConfig();
    this.createTransporter();
  }

  private validateConfig(): void {
    if (!this.config.user || !this.config.password) {
      throw new Error('Email configuration is incomplete. Please set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD');
    }
  }

  private createTransporter(): void {
    this.transporter = nodemailer.createTransport({
      host: this.config.host,
      port: this.config.port,
      secure: this.config.secure,
      auth: {
        user: this.config.user,
        pass: this.config.password
      },
      tls: {
        rejectUnauthorized: false
      }
    });
  }

  async verifyConnection(): Promise<boolean> {
    try {
      await this.transporter.verify();
      console.log('Email service connection verified successfully');
      return true;
    } catch (error) {
      console.error('Email service connection failed:', error);
      return false;
    }
  }

  private generateOTPEmailTemplate(otp: string, firstName: string, type: 'registration' | 'login'): string {
    const purpose = type === 'registration' ? 'complete your registration' : 'verify your login';
    const title = type === 'registration' ? 'Registration Verification' : 'Login Verification';
    
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${title}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9f9f9; }
        .otp-code { 
            background: #3498db; 
            color: white; 
            padding: 15px 30px; 
            font-size: 32px; 
            font-weight: bold; 
            text-align: center; 
            margin: 20px 0; 
            border-radius: 5px;
            letter-spacing: 5px;
        }
        .warning { color: #e74c3c; font-size: 14px; margin-top: 20px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Business Intelligence Assistant</h1>
            <h2>${title}</h2>
        </div>
        <div class="content">
            <p>Hello ${firstName},</p>
            <p>Use this verification code to ${purpose}:</p>
            <div class="otp-code">${otp}</div>
            <p>This code will expire in 10 minutes for security purposes.</p>
            <div class="warning">
                <strong>Security Notice:</strong> If you didn't request this verification code, please ignore this email. 
                Never share this code with anyone.
            </div>
        </div>
        <div class="footer">
            <p>This email was sent by ${this.config.fromName}</p>
            <p>If you have questions, please contact our support team.</p>
        </div>
    </div>
</body>
</html>`;
  }

  private generateWelcomeEmailTemplate(firstName: string, accountType: string, displayName: string): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to Business Intelligence Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #27ae60; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9f9f9; }
        .features { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .feature-item { margin: 15px 0; padding-left: 20px; }
        .cta-button { 
            background: #3498db; 
            color: white; 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block; 
            margin: 20px 0; 
        }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Business Intelligence Assistant!</h1>
        </div>
        <div class="content">
            <p>Hello ${firstName},</p>
            <p>Congratulations! Your ${accountType} account has been successfully verified and activated.</p>
            <p><strong>Account Details:</strong></p>
            <ul>
                <li>Display Name: ${displayName}</li>
                <li>Account Type: ${accountType.charAt(0).toUpperCase() + accountType.slice(1)}</li>
                <li>Email: [User's email will be shown here]</li>
            </ul>
            
            <div class="features">
                <h3>What you can do now:</h3>
                <div class="feature-item">📊 Upload CSV and Excel files for analysis</div>
                <div class="feature-item">🤖 Ask questions about your data in natural language</div>
                <div class="feature-item">📈 Generate interactive charts and visualizations</div>
                <div class="feature-item">💡 Get AI-powered business insights and recommendations</div>
                <div class="feature-item">📱 Access your dashboard from any device</div>
                <div class="feature-item">🔒 Secure two-factor authentication protection</div>
            </div>
            
            <p>Ready to start analyzing your business data?</p>
            <a href="#" class="cta-button">Access Your Dashboard</a>
            
            <div style="margin-top: 30px; padding: 15px; background: #ecf0f1; border-radius: 5px;">
                <h4>Security Features:</h4>
                <p>✅ Two-factor authentication enabled<br>
                ✅ Trusted device management<br>
                ✅ Secure data encryption<br>
                ✅ Regular security monitoring</p>
            </div>
        </div>
        <div class="footer">
            <p>Thank you for choosing ${this.config.fromName}</p>
            <p>Need help? Contact our support team anytime.</p>
        </div>
    </div>
</body>
</html>`;
  }

  private generateSecurityAlertTemplate(firstName: string, alertType: string, details: string): string {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Security Alert - Business Intelligence Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #e74c3c; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9f9f9; }
        .alert-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Alert</h1>
        </div>
        <div class="content">
            <p>Hello ${firstName},</p>
            <p>We detected ${alertType} on your Business Intelligence Assistant account.</p>
            
            <div class="alert-box">
                <strong>Details:</strong><br>
                ${details}
            </div>
            
            <p><strong>What should you do?</strong></p>
            <ul>
                <li>If this was you, no action is needed</li>
                <li>If this wasn't you, please secure your account immediately</li>
                <li>Consider changing your password</li>
                <li>Review your trusted devices</li>
            </ul>
            
            <p>If you have any concerns, please contact our security team immediately.</p>
        </div>
        <div class="footer">
            <p>This alert was sent for your account security</p>
            <p>${this.config.fromName} Security Team</p>
        </div>
    </div>
</body>
</html>`;
  }

  async sendOTPEmail(
    email: string, 
    otp: string, 
    firstName: string, 
    type: 'registration' | 'login'
  ): Promise<boolean> {
    try {
      const subject = type === 'registration' 
        ? 'Verify Your Registration - Business Intelligence Assistant' 
        : 'Login Verification Code - Business Intelligence Assistant';

      const htmlContent = this.generateOTPEmailTemplate(otp, firstName, type);

      await this.transporter.sendMail({
        from: `"${this.config.fromName}" <${this.config.fromEmail}>`,
        to: email,
        subject,
        html: htmlContent,
        text: `Your verification code is: ${otp}. This code will expire in 10 minutes.`
      });

      console.log(`${type} OTP email sent successfully to ${email}`);
      return true;
    } catch (error) {
      console.error(`Failed to send ${type} OTP email to ${email}:`, error);
      return false;
    }
  }

  async sendWelcomeEmail(
    email: string, 
    firstName: string, 
    accountType: string, 
    displayName: string
  ): Promise<boolean> {
    try {
      const htmlContent = this.generateWelcomeEmailTemplate(firstName, accountType, displayName);

      await this.transporter.sendMail({
        from: `"${this.config.fromName}" <${this.config.fromEmail}>`,
        to: email,
        subject: 'Welcome to Business Intelligence Assistant - Account Activated!',
        html: htmlContent,
        text: `Welcome ${firstName}! Your ${accountType} account has been successfully activated. You can now start analyzing your business data with our AI-powered assistant.`
      });

      console.log(`Welcome email sent successfully to ${email}`);
      return true;
    } catch (error) {
      console.error(`Failed to send welcome email to ${email}:`, error);
      return false;
    }
  }

  async sendSecurityAlert(
    email: string, 
    firstName: string, 
    alertType: string, 
    details: string
  ): Promise<boolean> {
    try {
      const htmlContent = this.generateSecurityAlertTemplate(firstName, alertType, details);

      await this.transporter.sendMail({
        from: `"${this.config.fromName} Security" <${this.config.fromEmail}>`,
        to: email,
        subject: `🔒 Security Alert - ${alertType}`,
        html: htmlContent,
        text: `Security Alert: ${alertType}. Details: ${details}. If this wasn't you, please secure your account immediately.`
      });

      console.log(`Security alert email sent successfully to ${email}`);
      return true;
    } catch (error) {
      console.error(`Failed to send security alert email to ${email}:`, error);
      return false;
    }
  }

  async sendTestEmail(email: string): Promise<boolean> {
    try {
      await this.transporter.sendMail({
        from: `"${this.config.fromName}" <${this.config.fromEmail}>`,
        to: email,
        subject: 'Email Service Test - Business Intelligence Assistant',
        html: '<h1>Email Service Test</h1><p>If you receive this email, the email service is working correctly.</p>',
        text: 'Email Service Test - If you receive this email, the email service is working correctly.'
      });

      console.log(`Test email sent successfully to ${email}`);
      return true;
    } catch (error) {
      console.error(`Failed to send test email to ${email}:`, error);
      return false;
    }
  }
}

// Export singleton instance
export const emailService = new EmailService();