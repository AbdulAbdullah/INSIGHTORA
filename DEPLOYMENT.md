# 🚀 Deployment Guide

This guide covers deploying your Bee Agent Chat application to various platforms.

## 🎯 Quick Deploy to Render

### Option 1: GitHub Integration (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `bee_agent_framework` repository

3. **Configure Settings**:
   - **Name**: `bee-agent-chat`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `.` (leave empty)
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

4. **Environment Variables**:
   - `NODE_ENV` = `production`
   - `GROQ_API_KEY` = `your_groq_api_key`
   - `PORT` = `3000` (auto-set by Render)

5. **Deploy**: Click "Create Web Service"

### Option 2: Manual Deploy

1. **Use render.yaml**:
   - Render will auto-detect the `render.yaml` file
   - Just set your `GROQ_API_KEY` in the dashboard

## 🐳 Docker Deployment

### Local Testing
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t bee-agent-chat .
docker run -p 3000:3000 --env-file .env bee-agent-chat
```

### Production Docker
```bash
# Build for production
docker build -t bee-agent-chat:prod .

# Run in production mode
docker run -p 3000:3000 \
  -e NODE_ENV=production \
  -e GROQ_API_KEY=your_key \
  bee-agent-chat:prod
```

## ☁️ Other Platform Deployments

### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway deploy
```

### Heroku
```bash
# Install Heroku CLI and login
heroku create bee-agent-chat-app
heroku config:set GROQ_API_KEY=your_key
git push heroku main
```

## 🔧 Environment Configuration

### Required Environment Variables
- `GROQ_API_KEY`: Your Groq API key (required)
- `NODE_ENV`: Set to `production` for production
- `PORT`: Server port (auto-set by most platforms)

### Optional Environment Variables
- `LOG_LEVEL`: Logging level (info, warn, error, debug)
- `GROQ_MODEL`: Model to use (default: llama-3.1-8b-instant)

## 🏥 Health Checks

Your app includes health check endpoints:
- `GET /health` - Basic health status
- `GET /api/info` - Detailed app information

## 📊 Monitoring

### Render Monitoring
- Built-in metrics and logs
- Custom health checks
- Auto-scaling options

### Custom Monitoring
```javascript
// Add to your monitoring service
const healthCheck = async () => {
  const response = await fetch('https://your-app.onrender.com/health');
  return response.ok;
};
```

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` to git
2. **API Keys**: Use platform environment variable management
3. **HTTPS**: All major platforms provide SSL by default
4. **CORS**: Configure if needed for custom domains

## 🚨 Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Environment Variables Not Working**:
- Check spelling and case sensitivity
- Verify in platform dashboard
- Restart the service after changes

**Health Check Failures**:
- Check `/health` endpoint responds
- Verify port configuration
- Check application logs

### Deployment Checklist

- [ ] Environment variables set
- [ ] Build command works locally
- [ ] Health check endpoint responding
- [ ] Static files served correctly
- [ ] WebSocket connections working
- [ ] API key valid and working

## 📈 Scaling

### Render Scaling
- **Starter Plan**: Good for development/testing
- **Standard Plan**: Production ready, auto-scaling
- **Pro Plan**: High performance, dedicated resources

### Performance Tips
- Use CDN for static assets
- Enable compression
- Monitor memory usage
- Scale based on concurrent users

## 🔄 Updates and Maintenance

### Automatic Deployments
- Connect GitHub for auto-deploy on push
- Use staging/production branches
- Set up proper CI/CD pipeline

### Manual Updates
```bash
# Update dependencies
npm update

# Test locally
npm run test

# Deploy
git push origin main  # (if auto-deploy enabled)
```

---

**Need Help?** Check the [main README](README.md) or create an issue!