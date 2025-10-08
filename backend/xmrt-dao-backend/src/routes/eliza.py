from flask import Blueprint, jsonify, request
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

eliza_bp = Blueprint('eliza', __name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def get_real_ai_response(message):
    """Get REAL AI response with multiple fallback models"""
    
    # Try OpenRouter with multiple models
    models_to_try = [
        "openchat/openchat-3.5-0106",
        "microsoft/wizardlm-2-8x22b",
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct"
    ]
    
    for model in models_to_try:
        try:
            if OPENROUTER_API_KEY:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://xmrtnet.onrender.com",
                    "X-Title": "XMRT DAO Eliza"
                }
                
                # Enhanced system prompt for better responses
                system_prompt = """You are Eliza, the advanced AI assistant for XMRT DAO. You are knowledgeable, helpful, and conversational. 

Key facts about XMRT:
- XMRT is a decentralized mining token that works even when internet infrastructure fails
- It uses mobile-friendly mining that continues during network outages
- XMRT DAO uses autonomous governance with token holder voting
- The treasury is managed through decentralized proposals
- Cross-chain functionality allows operation across multiple blockchains

Respond naturally and conversationally. Give detailed, helpful answers. Don't mention that you're "working on connecting to full AI capabilities" - you ARE the full AI capability."""

                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
                
                print(f"Trying model: {model}")
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                       headers=headers, json=data, timeout=30)
                
                print(f"OpenRouter response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                    print(f"SUCCESS with {model}: {ai_response[:100]}...")
                    return ai_response
                else:
                    print(f"Model {model} failed with {response.status_code}: {response.text}")
                    continue
                    
        except Exception as e:
            print(f"Exception with {model}: {str(e)}")
            continue
    
    # If all models fail, return None to trigger smart fallback
    return None

def get_smart_fallback(message):
    """Smart contextual responses based on keywords"""
    message_lower = message.lower()
    
    # Mining-related questions
    if any(word in message_lower for word in ["mine", "mining", "miner", "hash", "offline"]):
        return """XMRT mining is revolutionary because it's designed for resilience. Unlike traditional cryptocurrencies that require constant internet connectivity, XMRT can continue mining operations even during network outages or infrastructure failures.

Here's how it works:
• Mobile-optimized mining algorithms that work on smartphones and tablets
• Local mesh networking capabilities that allow miners to coordinate without internet
• Automatic synchronization when connectivity is restored
• Energy-efficient proof-of-work that doesn't drain mobile batteries

You can start mining by downloading the XMRT mobile app and joining the decentralized mining network. The system automatically adjusts difficulty based on network conditions and available miners."""

    # DAO and governance questions
    elif any(word in message_lower for word in ["dao", "governance", "voting", "proposal", "token"]):
        return """XMRT DAO operates as a truly decentralized autonomous organization where every decision is made by token holders through on-chain voting.

Our governance system includes:
• Proposal creation by any token holder with minimum stake
• Multi-phase voting with discussion periods
• Quadratic voting to prevent whale dominance  
• Automatic execution of passed proposals
• Treasury management through community decisions

Token holders can participate by staking XMRT tokens, which gives them voting power proportional to their stake and commitment to the network. All governance actions are transparent and recorded on the blockchain."""

    # Treasury and economics
    elif any(word in message_lower for word in ["treasury", "token", "economic", "revenue", "fund"]):
        return """The XMRT DAO treasury is managed entirely by the community through decentralized governance. Our economic model is designed for long-term sustainability and growth.

Treasury features:
• Multi-signature wallet controlled by elected community members
• Revenue from mining fees, transaction fees, and partnership agreements
• Transparent allocation through community proposals
• Emergency funds for network security and development
• Yield generation through DeFi protocols (when approved by governance)

The tokenomics incentivize both mining participation and long-term holding, creating a balanced ecosystem that rewards contributors while maintaining network security."""

    # Technical and cross-chain
    elif any(word in message_lower for word in ["technical", "blockchain", "cross-chain", "interop"]):
        return """XMRT's technical architecture is built for interoperability and resilience across multiple blockchain networks.

Technical highlights:
• Layer Zero integration for seamless cross-chain transfers
• Smart contract compatibility with Ethereum, BSC, and Polygon
• Hybrid consensus mechanism combining PoW mining with PoS validation
• Advanced cryptographic techniques for offline operation
• Automatic bridge protocols for asset movement

The cross-chain functionality means you can use XMRT tokens on any supported network while maintaining the same mining rewards and governance rights. This creates unprecedented flexibility for users and developers."""

    # Default intelligent response
    else:
        return f"""I understand you're asking about: "{message}"

As the XMRT DAO assistant, I'm here to help you navigate our decentralized ecosystem. XMRT represents a new paradigm in cryptocurrency - one that prioritizes resilience, community governance, and practical utility.

Whether you're interested in:
• Starting mobile mining operations
• Participating in DAO governance 
• Understanding our tokenomics
• Exploring cross-chain capabilities
• Learning about decentralized systems

I'm equipped to provide detailed, practical guidance. What specific aspect would you like to explore further?"""

@eliza_bp.route('/eliza', methods=['POST'])
def chat_with_eliza():
    """Enhanced chat endpoint with REAL AI"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Try to get real AI response first
        ai_response = get_real_ai_response(message)
        
        if ai_response:
            return jsonify({"response": ai_response, "source": "openrouter"})
        else:
            # Use smart fallback instead of generic template
            smart_response = get_smart_fallback(message)
            return jsonify({"response": smart_response, "source": "smart_fallback"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eliza_bp.route('/eliza/health', methods=['GET'])
def eliza_health():
    """Health check for Eliza"""
    return jsonify({
        "status": "online",
        "service": "Eliza DAO Assistant",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "version": "enhanced-ai-v2"
    })


@eliza_bp.route('/eliza/activity', methods=['GET'])
def get_eliza_activity():
    """Get recent Eliza activity from GitHub repository"""
    try:
        from github import Github, Auth
        
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            return jsonify({
                "error": "GitHub token not configured",
                "activities": []
            }), 500
        
        # Initialize GitHub client
        github = Github(auth=Auth.Token(github_token))
        repo = github.get_user('DevGruGold').get_repo('xmrtnet')
        
        # Get recent commits by Eliza
        activities = []
        commits = repo.get_commits(author='eliza@xmrt.io')[:20]  # Last 20 commits
        
        for commit in commits:
            activity = {
                "type": "commit",
                "message": commit.commit.message,
                "timestamp": commit.commit.author.date.isoformat(),
                "sha": commit.sha[:8],
                "url": commit.html_url,
                "files_changed": len(commit.files) if commit.files else 0
            }
            
            # Categorize activity type based on commit message
            message_lower = commit.commit.message.lower()
            if "self-analysis" in message_lower or "self-improvement" in message_lower:
                activity["category"] = "self_improvement"
                activity["icon"] = "🧠"
            elif "tool discovery" in message_lower or "tools found" in message_lower:
                activity["category"] = "tool_discovery"
                activity["icon"] = "🔍"
            elif "utility" in message_lower or "built" in message_lower:
                activity["category"] = "utility_creation"
                activity["icon"] = "🛠️"
            elif "cycle" in message_lower:
                activity["category"] = "cycle_completion"
                activity["icon"] = "🔄"
            else:
                activity["category"] = "general"
                activity["icon"] = "📝"
            
            activities.append(activity)
        
        # Get current state from eliza_state.json
        try:
            state_file = repo.get_contents("eliza_state.json")
            state_data = json.loads(state_file.decoded_content.decode())
            
            return jsonify({
                "status": "success",
                "activities": activities,
                "state": {
                    "cycle_count": state_data.get('cycle_count', 0),
                    "last_run": state_data.get('last_run'),
                    "total_improvements": state_data.get('total_improvements', 0),
                    "total_tools_discovered": state_data.get('total_tools_discovered', 0),
                    "total_utilities_built": state_data.get('total_utilities_built', 0)
                }
            })
        except Exception as e:
            print(f"Error fetching state: {e}")
            return jsonify({
                "status": "success",
                "activities": activities,
                "state": None
            })
        
    except Exception as e:
        print(f"Error fetching activity: {e}")
        return jsonify({
            "error": str(e),
            "activities": []
        }), 500

@eliza_bp.route('/eliza/stats', methods=['GET'])
def get_eliza_stats():
    """Get Eliza performance statistics"""
    try:
        from github import Github, Auth
        
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            return jsonify({"error": "GitHub token not configured"}), 500
        
        github = Github(auth=Auth.Token(github_token))
        repo = github.get_user('DevGruGold').get_repo('xmrtnet')
        
        # Get state
        state_file = repo.get_contents("eliza_state.json")
        state_data = json.loads(state_file.decoded_content.decode())
        
        # Count reports
        reports_dir = repo.get_contents("reports")
        report_files = [f for f in reports_dir if f.name.endswith('.md')]
        
        # Count utilities
        utilities_dir = repo.get_contents("utilities")
        utility_files = [f for f in utilities_dir if f.name.endswith('.py')]
        
        # Get recent commits count
        commits = list(repo.get_commits(author='eliza@xmrt.io')[:100])
        
        return jsonify({
            "status": "success",
            "stats": {
                "cycle_count": state_data.get('cycle_count', 0),
                "total_commits": len(commits),
                "total_reports": len(report_files),
                "total_utilities": len(utility_files),
                "total_improvements": state_data.get('total_improvements', 0),
                "total_tools_discovered": state_data.get('total_tools_discovered', 0),
                "last_run": state_data.get('last_run'),
                "uptime_status": "active" if state_data.get('last_run') else "initializing"
            }
        })
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({
            "error": str(e),
            "stats": {}
        }), 500
