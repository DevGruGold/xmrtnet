# Eliza Autonomous Agent - Flask Application

## Structure

- `main.py` - Flask application entry point
- `routes/` - API endpoint definitions
- `services/` - Business logic and agent implementation
- `models/` - Data models (future)
- `utils/` - Utility functions (future)

## Running Locally

```bash
# Install dependencies
pip install -r ../requirements.txt

# Set environment variables
export GITHUB_TOKEN=your_token
export GITHUB_USER=DevGruGold
export TARGET_REPO=xmrtnet

# Run the application
python main.py
```

## API Endpoints

- `GET /` - Service information
- `GET /api/health` - Health check
- `GET /api/status` - Agent status
- `GET /api/logs` - Activity logs
- `POST /api/start` - Start agent
- `POST /api/stop` - Stop agent
- `GET /api/metrics` - Performance metrics
- `GET /api/config` - Configuration

## Deployment

See `docs/FLASK_DEPLOYMENT_GUIDE.md` for deployment instructions.
