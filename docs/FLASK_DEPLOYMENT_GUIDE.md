# Eliza Autonomous Agent - Flask Web Service Deployment Guide

## Overview

The Eliza autonomous agent has been refactored into a Flask web service architecture suitable for Render deployment. This guide explains the new structure and deployment process.

## Architecture

### Directory Structure

```
xmrtnet/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Flask application entry point
│   ├── routes/
│   │   └── api.py                 # API endpoints
│   ├── services/
│   │   └── eliza_agent.py         # Core agent logic
│   ├── models/                    # (Future: Data models)
│   └── utils/                     # (Future: Utility functions)
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render deployment configuration
└── docs/
    └── FLASK_DEPLOYMENT_GUIDE.md  # This file
```

### Components

#### 1. Flask Application (`app/main.py`)
- Main application factory
- CORS configuration for frontend
- Blueprint registration
- Error handlers
- Root endpoint with API documentation

#### 2. API Routes (`app/routes/api.py`)
- `/api/health` - Health check for Render
- `/api/status` - Get agent status and metrics
- `/api/logs` - Get activity logs
- `/api/start` - Start the autonomous agent
- `/api/stop` - Stop the autonomous agent
- `/api/metrics` - Get performance metrics
- `/api/config` - Get current configuration

#### 3. Eliza Agent Service (`app/services/eliza_agent.py`)
- Core autonomous agent logic
- GitHub integration
- AI capabilities (Gemini)
- 24/7 continuous operation
- Background thread execution
- State management
- Activity logging

### Key Features

✅ **Separated Concerns**: Business logic separated from web service layer  
✅ **RESTful API**: Clean API endpoints for frontend integration  
✅ **Background Processing**: Agent runs in background thread  
✅ **Real-time Logs**: Activity logs accessible via API  
✅ **Health Checks**: Render-compatible health endpoint  
✅ **CORS Enabled**: Frontend can connect from any origin  
✅ **Thread-Safe**: Proper synchronization for concurrent access  

## Deployment to Render

### Prerequisites

1. GitHub repository with the code
2. Render account
3. GitHub Personal Access Token with repo permissions
4. (Optional) Gemini API key for AI enhancement

### Step 1: Push Code to GitHub

The code has been structured and is ready to push:

```bash
git add app/ requirements.txt render.yaml docs/
git commit -m "Refactor Eliza to Flask web service architecture"
git push origin main
```

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

   **Basic Settings:**
   - Name: `eliza-autonomous-agent`
   - Environment: `Python 3`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: Leave blank (or specify if needed)

   **Build & Deploy:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

   **Health Check:**
   - Health Check Path: `/api/health`

### Step 3: Configure Environment Variables

Add these environment variables in Render:

**Required:**
```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USER=DevGruGold
TARGET_REPO=xmrtnet
```

**Optional:**
```
ECOSYSTEM_REPO=XMRT-Ecosystem
ELIZA_MODE=continuous_24_7
CYCLE_INTERVAL=3600
MAX_CYCLES=0
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_flask_secret_key
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the Flask application
   - Assign a public URL

### Step 5: Verify Deployment

Once deployed, test the endpoints:

```bash
# Health check
curl https://your-app.onrender.com/api/health

# Get status
curl https://your-app.onrender.com/api/status

# Start agent
curl -X POST https://your-app.onrender.com/api/start

# View logs
curl https://your-app.onrender.com/api/logs
```

## Frontend Integration

### Update Frontend API URL

In the frontend dashboard (`eliza-dashboard/src/App.jsx`), update the API URL:

```javascript
const [apiUrl, setApiUrl] = useState('https://your-app.onrender.com')
```

Or use the configuration UI to set it dynamically.

### Rebuild and Redeploy Frontend

```bash
cd frontend/eliza-dashboard
pnpm run build
# Deploy the dist/ directory to your hosting service
```

## API Documentation

### GET /api/health

Health check endpoint for Render.

**Response:**
```json
{
  "status": "healthy",
  "service": "eliza-autonomous-agent",
  "version": "3.0"
}
```

### GET /api/status

Get current agent status and metrics.

**Response:**
```json
{
  "is_running": true,
  "current_cycle": 5,
  "metrics": {
    "cycles_completed": 5,
    "self_improvements": 12,
    "ecosystem_improvements": 8,
    "tools_discovered": 15,
    "utilities_built": 6,
    "github_commits": 25,
    "ecosystem_commits": 10,
    "uptime_start": "2025-10-09T12:00:00",
    "last_cycle_time": "2025-10-09T13:00:00",
    "last_cycle_duration": 45.2,
    "status": "running"
  },
  "config": {
    "github_user": "DevGruGold",
    "target_repo": "xmrtnet",
    "ecosystem_repo": "XMRT-Ecosystem",
    "cycle_interval": 3600,
    "max_cycles": 0,
    "mode": "continuous_24_7",
    "ai_enabled": true
  }
}
```

### GET /api/logs?limit=50

Get recent activity logs.

**Parameters:**
- `limit` (optional): Number of logs to return (default: 50)

**Response:**
```json
{
  "logs": [
    {
      "time": "2025-10-09T13:00:00",
      "level": "info",
      "message": "Starting cycle 5"
    },
    {
      "time": "2025-10-09T13:00:45",
      "level": "success",
      "message": "Cycle 5 completed in 45.2s"
    }
  ]
}
```

### POST /api/start

Start the autonomous agent.

**Response:**
```json
{
  "success": true,
  "message": "Agent started successfully"
}
```

### POST /api/stop

Stop the autonomous agent.

**Response:**
```json
{
  "success": true,
  "message": "Agent stopped successfully"
}
```

### GET /api/metrics

Get performance metrics only.

**Response:**
```json
{
  "cycles_completed": 5,
  "self_improvements": 12,
  "ecosystem_improvements": 8,
  "tools_discovered": 15,
  "utilities_built": 6,
  "github_commits": 25,
  "ecosystem_commits": 10,
  "uptime_start": "2025-10-09T12:00:00",
  "last_cycle_time": "2025-10-09T13:00:00",
  "last_cycle_duration": 45.2,
  "status": "running"
}
```

### GET /api/config

Get current configuration.

**Response:**
```json
{
  "github_user": "DevGruGold",
  "target_repo": "xmrtnet",
  "ecosystem_repo": "XMRT-Ecosystem",
  "cycle_interval": 3600,
  "max_cycles": 0,
  "mode": "continuous_24_7",
  "ai_enabled": true
}
```

## How It Works

### Agent Lifecycle

1. **Initialization**: When the Flask app starts, the agent is initialized but not running
2. **Start**: POST to `/api/start` starts the agent in a background thread
3. **Continuous Operation**: Agent runs enhancement cycles at configured intervals
4. **Monitoring**: Frontend polls `/api/status` and `/api/logs` for updates
5. **Stop**: POST to `/api/stop` gracefully stops the agent

### Background Thread

The agent runs in a daemon thread that:
- Executes enhancement cycles continuously
- Updates metrics in real-time
- Logs all activities
- Can be started/stopped via API
- Survives web request timeouts

### State Management

- Agent state is maintained in memory
- Metrics are updated after each cycle
- Logs are kept in a rolling buffer (last 100 entries)
- State persists as long as the service is running

## Monitoring

### Render Dashboard

Monitor your service in Render:
- View logs in real-time
- Check resource usage
- Monitor health checks
- View deployment history

### Frontend Dashboard

Use the web dashboard to:
- Start/stop the agent
- View real-time metrics
- Monitor activity logs
- Check configuration

### GitHub Repository

Check the repository for:
- New cycle reports in `reports/` directory
- Commits from "Eliza Autonomous"
- Updates to `eliza_state.json`

## Troubleshooting

### Agent Not Starting

**Problem**: POST to `/api/start` returns error

**Solutions**:
1. Check GitHub token is valid
2. Verify repository access
3. Check environment variables
4. Review logs in Render dashboard

### Health Check Failing

**Problem**: Render shows service as unhealthy

**Solutions**:
1. Verify `/api/health` endpoint is accessible
2. Check if Flask app is running
3. Review application logs
4. Ensure port binding is correct

### Frontend Can't Connect

**Problem**: Frontend shows "Disconnected"

**Solutions**:
1. Verify API URL is correct
2. Check CORS is enabled
3. Ensure service is running
4. Test endpoints with curl

### High Memory Usage

**Problem**: Service using too much memory

**Solutions**:
1. Increase cycle interval
2. Reduce log buffer size
3. Upgrade Render plan
4. Optimize agent operations

## Best Practices

### Security

- ✅ Store secrets in environment variables
- ✅ Never commit tokens to repository
- ✅ Use HTTPS for all API calls
- ✅ Rotate tokens regularly

### Performance

- ✅ Use appropriate cycle intervals (3600s recommended)
- ✅ Monitor GitHub API rate limits
- ✅ Keep log buffer size reasonable
- ✅ Use gunicorn with 2 workers

### Reliability

- ✅ Enable auto-deploy in Render
- ✅ Monitor health checks
- ✅ Review logs regularly
- ✅ Test endpoints after deployment

## Scaling

### Horizontal Scaling

Render can scale your service:
- Increase number of instances
- Load balance across regions
- Auto-scale based on traffic

### Vertical Scaling

Upgrade your Render plan for:
- More CPU and memory
- Better performance
- Higher reliability

## Support

For issues or questions:
1. Check Render logs
2. Review GitHub repository
3. Test API endpoints
4. Contact development team

---

**Version**: 3.0  
**Last Updated**: 2025-10-09  
**Architecture**: Flask Web Service with Background Agent  
**Deployment**: Render Web Service

