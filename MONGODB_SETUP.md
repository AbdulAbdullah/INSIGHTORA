# MongoDB Setup Guide

## Option 1: MongoDB Atlas (Cloud) - RECOMMENDED for Development

1. Go to https://cloud.mongodb.com/
2. Create a free account
3. Create a new cluster (free tier available)
4. Create a database user:
   - Username: `biassistant`
   - Password: `SecurePass123` (or generate a secure password)
5. Get your connection string:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

Example connection string:
```
mongodb+srv://biassistant:SecurePass123@cluster0.xxxxx.mongodb.net/bi_assistant?retryWrites=true&w=majority
```

## Option 2: Local MongoDB (If you have MongoDB installed)

1. Start MongoDB service:
   ```bash
   # Windows (run as administrator)
   net start MongoDB
   
   # Or start mongod directly
   mongod --dbpath C:\data\db
   ```

2. Create database and user:
   ```bash
   # Connect to MongoDB shell
   mongo
   
   # Create database and user
   use bi_assistant
   db.createUser({
     user: "biassistant",
     pwd: "SecurePass123",
     roles: [{ role: "readWrite", db: "bi_assistant" }]
   })
   ```

3. Update .env file:
   ```
   MONGODB_URI=mongodb://biassistant:SecurePass123@localhost:27017/bi_assistant?authSource=bi_assistant
   ```

## Option 3: Use In-Memory Database for Testing

For testing purposes, we can modify the code to use an in-memory database or mock data.