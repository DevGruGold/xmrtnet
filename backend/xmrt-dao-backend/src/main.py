import os
import sys
from dotenv import load_dotenv

load_dotenv()
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.memory import db as memory_db, ElizaMemory, ConversationHistory, MemoryAssociation
from src.utils.memory_manager import memory_manager
from src.routes.user import user_bp
from src.routes.blockchain import blockchain_bp
from src.routes.eliza import eliza_bp
from src.routes.ai_agents import ai_agents_bp
from src.routes.storage import storage_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
app.register_blueprint(eliza_bp, url_prefix='/api/eliza')
app.register_blueprint(ai_agents_bp, url_prefix='/api/ai-agents')
app.register_blueprint(storage_bp, url_prefix='/api/storage')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
memory_db.init_app(app)

# Initialize memory manager
memory_manager.init_app(app)

with app.app_context():
    db.create_all()  # Creates user tables
    memory_db.create_all()  # Creates memory tables

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
