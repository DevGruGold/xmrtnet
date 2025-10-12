"""
Eliza Autonomous Agent - Flask Web Service
Main application entry point for Render deployment
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'eliza-autonomous-agent-secret')
    app.config['JSON_SORT_KEYS'] = False
    
    # Register blueprints
    from app.routes.api import api
    app.register_blueprint(api)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Eliza Autonomous Agent',
            'version': '3.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'status': '/api/status',
                'logs': '/api/logs',
                'metrics': '/api/metrics',
                'config': '/api/config',
                'start': '/api/start (POST)',
                'stop': '/api/stop (POST)'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

