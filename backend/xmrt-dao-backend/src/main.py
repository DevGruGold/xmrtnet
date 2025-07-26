import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

# Import only the simplified eliza blueprint
from src.routes.eliza import eliza_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'temp-secret-key-12345')

# Enable CORS for all routes
CORS(app)

# Register the eliza blueprint
app.register_blueprint(eliza_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return jsonify({
        "status": "Flask Eliza API is running",
        "version": "minimal-v1",
        "endpoints": ["/api/eliza", "/api/eliza/health"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
