"""
API Routes for Eliza Agent Web Service
"""

from flask import Blueprint, jsonify, request
from app.services.eliza_agent import ElizaAgent

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Global agent instance
agent = None

def init_agent():
    """Initialize the agent instance"""
    global agent
    if agent is None:
        agent = ElizaAgent()
    return agent

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'eliza-autonomous-agent',
        'version': '3.0'
    }), 200

@api.route('/status', methods=['GET'])
def get_status():
    """Get agent status"""
    agent = init_agent()
    status = agent.get_status()
    return jsonify(status), 200

@api.route('/logs', methods=['GET'])
def get_logs():
    """Get activity logs"""
    agent = init_agent()
    limit = request.args.get('limit', 50, type=int)
    logs = agent.get_logs(limit)
    return jsonify({'logs': logs}), 200

@api.route('/start', methods=['POST'])
def start_agent():
    """Start the autonomous agent"""
    agent = init_agent()
    success = agent.start()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Agent started successfully'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Agent already running or failed to start'
        }), 400

@api.route('/stop', methods=['POST'])
def stop_agent():
    """Stop the autonomous agent"""
    agent = init_agent()
    success = agent.stop()
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Agent stopped successfully'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Agent not running'
        }), 400

@api.route('/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    agent = init_agent()
    status = agent.get_status()
    return jsonify(status['metrics']), 200

@api.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    agent = init_agent()
    status = agent.get_status()
    return jsonify(status['config']), 200

