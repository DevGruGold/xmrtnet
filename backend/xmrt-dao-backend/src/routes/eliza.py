from flask import Blueprint, jsonify, request
import os
from dotenv import load_dotenv
import requests

load_dotenv()

eliza_bp = Blueprint('eliza', __name__)

# Comment out all database and complex dependencies for now
# import openai
# from src.utils.memory_manager import memory_manager
# from src.models.memory import MemoryType, AssociationType

# OpenRouter fallback (only dependency we'll use)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def get_simple_ai_response(message):
    """Simple AI response with OpenRouter only"""
    try:
        if OPENROUTER_API_KEY:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "openchat/openchat-3.5-0106",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7
            }
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                   headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenRouter failed: {e}")
    
    # Fallback response if all APIs fail
    return f"Hello! I'm Eliza, the XMRT DAO assistant. You asked: '{message}'. I'm currently in simplified mode while we configure the full AI integration."

@eliza_bp.route('/eliza', methods=['POST'])
def chat_with_eliza():
    """Simple chat endpoint"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        response = get_simple_ai_response(message)
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eliza_bp.route('/eliza/health', methods=['GET'])
def eliza_health():
    """Health check for Eliza"""
    return jsonify({
        "status": "online",
        "service": "Eliza DAO Assistant",
        "openrouter_configured": bool(OPENROUTER_API_KEY)
    })
