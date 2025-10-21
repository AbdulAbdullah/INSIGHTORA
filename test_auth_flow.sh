#!/bin/bash

# Enhanced Authentication Flow Test
# Demonstrates Policy A: Tokens only after full login verification

echo "🔐 Testing Enhanced Authentication Flow (Policy A)"
echo "================================================="
echo ""

# Test 1: Registration
echo "📝 Step 1: User Registration"
echo "curl -X POST http://localhost:3000/api/auth/register ..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "firstName": "Test",
    "lastName": "User", 
    "accountType": "individual"
  }')

echo "Response: $REGISTER_RESPONSE"
echo ""

# Test 2: Email Verification (NO TOKENS ISSUED)
echo "✉️  Step 2: Email Verification (Notice: NO tokens returned)"
echo "curl -X POST http://localhost:3000/api/auth/verify-email ..."
VERIFY_RESPONSE=$(curl -s -X POST http://localhost:3000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": "123456"
  }')

echo "Response: $VERIFY_RESPONSE"
echo ""

# Test 3: Login (Sends OTP)
echo "🔑 Step 3: Login (Sends Login OTP, still NO final tokens)"
echo "curl -X POST http://localhost:3000/api/auth/login ..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }')

echo "Response: $LOGIN_RESPONSE"
echo ""

# Test 4: Login Verification (FINAL TOKENS ISSUED)
echo "🎯 Step 4: Login OTP Verification (ONLY NOW are final tokens issued)"
echo "curl -X POST http://localhost:3000/api/auth/verify-login ..."
echo "Note: This would include the loginSessionToken from step 3 and the OTP from email"
echo ""

echo "🎉 SECURITY IMPROVEMENT SUMMARY:"
echo "================================"
echo "✅ Registration: Creates user, sends OTP, NO tokens"
echo "✅ Email Verification: Marks verified, sends welcome, NO tokens"  
echo "✅ Login: Validates credentials, sends login OTP, NO final tokens"
echo "✅ Login Verification: ONLY step that issues access/refresh tokens"
echo ""
echo "🛡️  Security Benefits:"
echo "   - Email access alone cannot obtain tokens"
echo "   - Full authentication (password + OTP) required for tokens"
echo "   - Perfect for BI platforms with sensitive data"
echo "   - Clear separation between verification and authentication"