#!/bin/bash
# Eliza Autonomous Agent Startup Script

echo "Starting Eliza Autonomous Agent..."
echo "=================================="

# Check for required environment variables
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN environment variable is required"
    exit 1
fi

# Set defaults
export GITHUB_USER="${GITHUB_USER:-DevGruGold}"
export TARGET_REPO="${TARGET_REPO:-xmrtnet}"
export ECOSYSTEM_REPO="${ECOSYSTEM_REPO:-XMRT-Ecosystem}"
export ELIZA_MODE="${ELIZA_MODE:-continuous_24_7}"
export CYCLE_INTERVAL="${CYCLE_INTERVAL:-3600}"
export MAX_CYCLES="${MAX_CYCLES:-0}"

echo "Configuration:"
echo "  GitHub User: $GITHUB_USER"
echo "  Target Repo: $TARGET_REPO"
echo "  Ecosystem Repo: $ECOSYSTEM_REPO"
echo "  Mode: $ELIZA_MODE"
echo "  Cycle Interval: ${CYCLE_INTERVAL}s"
echo "  Max Cycles: ${MAX_CYCLES}"
echo ""

# Install dependencies if needed
if ! python3 -c "import github" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run the agent
echo "Starting agent..."
python3 src/autonomous_eliza_continuous.py
