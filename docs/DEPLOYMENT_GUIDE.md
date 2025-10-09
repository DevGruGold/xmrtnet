# Eliza Autonomous Agent - Deployment Guide

## Overview

This guide explains how to deploy the enhanced Eliza autonomous agent with 24/7 continuous operation capabilities.

## Architecture

The system consists of two main components:

1. **Backend Agent** (`src/autonomous_eliza_continuous.py`)
   - Python-based autonomous agent
   - Runs continuously in 24/7 mode
   - Performs self-improvement cycles
   - Manages dual repositories (xmrtnet + XMRT-Ecosystem)

2. **Frontend Dashboard** (`frontend/eliza-dashboard/`)
   - React-based web interface
   - Configuration management
   - Real-time monitoring
   - Deployment controls

## Deployment Options

### Option 1: Render (Recommended)

#### Backend Deployment

1. Create a new Background Worker on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip3 install -r requirements.txt`
   - **Start Command**: `python3 src/autonomous_eliza_continuous.py`
4. Set environment variables:
   ```
   GITHUB_TOKEN=your_github_token
   GITHUB_USER=DevGruGold
   TARGET_REPO=xmrtnet
   ECOSYSTEM_REPO=XMRT-Ecosystem
   GEMINI_API_KEY=your_gemini_key (optional)
   ELIZA_MODE=continuous_24_7
   CYCLE_INTERVAL=3600
   MAX_CYCLES=0
   ```

#### Frontend Deployment

1. Create a new Static Site on Render
2. Configure:
   - **Build Command**: `cd frontend/eliza-dashboard && pnpm install && pnpm run build`
   - **Publish Directory**: `frontend/eliza-dashboard/dist`

### Option 2: GitHub Actions (Scheduled)

Create `.github/workflows/eliza-agent.yml`:

```yaml
name: Eliza Autonomous Agent

on:
  schedule:
    - cron: '0 * * * *'  # Run every hour
  workflow_dispatch:

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install PyGithub google-generativeai requests
      
      - name: Run Eliza Agent
        env:
          GITHUB_TOKEN: ${{ secrets.ELIZA_GITHUB_TOKEN }}
          GITHUB_USER: DevGruGold
          TARGET_REPO: xmrtnet
          ECOSYSTEM_REPO: XMRT-Ecosystem
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ELIZA_MODE: self_improvement
        run: python3 src/autonomous_eliza_continuous.py
```

### Option 3: Local Server (Development)

```bash
# Install dependencies
pip3 install PyGithub google-generativeai requests

# Set environment variables
export GITHUB_TOKEN="your_token"
export GITHUB_USER="DevGruGold"
export TARGET_REPO="xmrtnet"
export ECOSYSTEM_REPO="XMRT-Ecosystem"
export ELIZA_MODE="continuous_24_7"
export CYCLE_INTERVAL="3600"

# Run the agent
python3 src/autonomous_eliza_continuous.py
```

## Environment Variables

### Required

- `GITHUB_TOKEN`: GitHub Personal Access Token with repo permissions
- `GITHUB_USER`: GitHub username (default: DevGruGold)
- `TARGET_REPO`: Primary repository name (default: xmrtnet)

### Optional

- `ECOSYSTEM_REPO`: Secondary repository name (default: XMRT-Ecosystem)
- `GEMINI_API_KEY`: Google Gemini API key for AI-enhanced analysis
- `ELIZA_GMAIL_USERNAME`: Gmail username for email notifications
- `ELIZA_GMAIL_PASSWORD`: Gmail app password for email notifications
- `ELIZA_MODE`: Operation mode (default: continuous_24_7)
  - `continuous_24_7`: Run continuously with scheduled cycles
  - `production`: Production mode with continuous operation
  - `self_improvement`: Single improvement cycle
- `CYCLE_INTERVAL`: Seconds between cycles (default: 3600)
- `MAX_CYCLES`: Maximum cycles to run, 0 = infinite (default: 0)

## Monitoring

### Activity Reports

Eliza generates comprehensive reports in the `reports/` directory:

- `self_analysis_cycle_N.md`: Self-analysis reports
- `tool_discovery_cycle_N.md`: Tool discovery reports
- `enhancement_cycle_N.md`: Complete cycle reports

### GitHub Discussions

Eliza posts cycle summaries to GitHub Discussions (or Issues) for transparency.

### State Persistence

Agent state is saved in `eliza_state.json`:
- Cycle count
- Last run timestamp
- Performance metrics
- Improvement history

## Troubleshooting

### Agent Not Starting

1. Check GitHub token permissions
2. Verify repository access
3. Check environment variables
4. Review error logs

### Rate Limiting

If you encounter GitHub API rate limits:
- Increase `CYCLE_INTERVAL`
- Reduce tool discovery scope
- Use authenticated requests (already implemented)

### Memory Issues

For long-running instances:
- Monitor memory usage
- Consider restarting periodically
- Adjust `MAX_CYCLES` to limit runtime

## Best Practices

1. **Security**
   - Never commit tokens to repository
   - Use environment variables for secrets
   - Rotate tokens regularly

2. **Performance**
   - Start with longer cycle intervals (3600s)
   - Monitor GitHub API usage
   - Review generated reports regularly

3. **Maintenance**
   - Check agent status daily
   - Review improvement suggestions
   - Update dependencies regularly

## Support

For issues or questions:
1. Check the logs in `reports/` directory
2. Review GitHub Issues
3. Contact the development team

---

Last updated: 2025-10-09T02:53:10.417656
Version: 3.0 (24/7 Continuous Operation)
