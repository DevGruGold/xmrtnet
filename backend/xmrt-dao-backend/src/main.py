import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS

# Import only the eliza blueprint (skip database-dependent ones)
try:
    from src.routes.eliza import eliza_bp
    ELIZA_AVAILABLE = True
except ImportError:
    ELIZA_AVAILABLE = False
    print("Warning: Eliza routes not available")

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'temp-secret-key')

# Enable CORS for all routes
CORS(app)

# Register only the eliza blueprint
if ELIZA_AVAILABLE:
    app.register_blueprint(eliza_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return {"status": "Flask Eliza API is running", "eliza_available": ELIZA_AVAILABLE}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
