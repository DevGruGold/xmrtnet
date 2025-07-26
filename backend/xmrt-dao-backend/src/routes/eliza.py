from flask import Blueprint, jsonify, request
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

eliza_bp = Blueprint('eliza', __name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def get_ai_response(message):
    """AI response with detailed error logging"""
    try:
        if not OPENROUTER_API_KEY:
            print("No OpenRouter API key found")
            return None
            
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://xmrtnet.onrender.com",
            "X-Title": "XMRT DAO Eliza"
        }
        data = {
            "model": "openchat/openchat-3.5-0106",
            "messages": [
                {"role": "system", "content": "You are Eliza, the AI assistant for XMRT DAO. Help users understand DAOs, governance, and decentralized systems."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        print(f"Calling OpenRouter with message: {message}")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                               headers=headers, json=data, timeout=30)
        
        print(f"OpenRouter status: {response.status_code}")
        print(f"OpenRouter response: {response.text[:200]}")
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenRouter error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"OpenRouter exception: {str(e)}")
        return None

@eliza_bp.route('/eliza', methods=['POST'])
def chat_with_eliza():
    """Enhanced chat endpoint with better AI integration"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Try to get AI response
        ai_response = get_ai_response(message)
        
        if ai_response:
            return jsonify({"response": ai_response, "source": "openrouter"})
        else:
            # Enhanced fallback with DAO knowledge
            fallback_responses = {
                "dao": "A DAO (Decentralized Autonomous Organization) is a blockchain-based organization governed by smart contracts and token holders, without traditional management hierarchy.",
                "governance": "DAO governance allows token holders to vote on proposals, treasury management, and protocol changes through decentralized voting mechanisms.",
                "xmrt": "XMRT is a decentralized mining token that continues to function even when traditional internet infrastructure fails, ensuring resilient blockchain operations.",
                "mining": "XMRT mining can be performed on mobile devices and continues to operate during network disruptions, making it ideal for distributed, resilient mining operations."
            }
            
            # Simple keyword matching for better fallback responses
            message_lower = message.lower()
            for keyword, response in fallback_responses.items():
                if keyword in message_lower:
                    return jsonify({"response": response, "source": "fallback"})
            
            return jsonify({
                "response": f"Hello! I'm Eliza, the XMRT DAO assistant. You asked about: '{message}'. While I'm working on connecting to my full AI capabilities, I can help you with questions about DAOs, governance, XMRT mining, and decentralized systems.",
                "source": "fallback"
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eliza_bp.route('/eliza/health', methods=['GET'])
def eliza_health():
    """Health check for Eliza"""
    return jsonify({
        "status": "online",
        "service": "Eliza DAO Assistant",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "version": "enhanced-v1"
    })
