import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="XMRT DAO - Decentralized Future",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown('''
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .agent-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
    
    .user-message {
        background: #667eea;
        color: white;
        padding: 0.8rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .agent-message {
        background: #e9ecef;
        color: #333;
        padding: 0.8rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        border-left: 3px solid #28a745;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
''', unsafe_allow_html=True)

# Header
st.markdown('''
<div class="main-header">
    <h1>🌐 XMRT DAO</h1>
    <h3>The Token That Mines When the Internet Dies</h3>
    <p>Decentralized • Autonomous • Resilient</p>
</div>
''', unsafe_allow_html=True)

# Sidebar for agent status
with st.sidebar:
    st.markdown("## 🤖 Agent Status")
    
    # Check agent health
    agents = [
        {"name": "Eliza", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🧠"},
        {"name": "DAO Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🏛️"},
        {"name": "Mining Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "⛏️"},
        {"name": "Treasury Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "💰"},
        {"name": "Governance Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🗳️"}
    ]
    
    for agent in agents:
        try:
            response = requests.get(agent["endpoint"], timeout=5)
            status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
        except:
            status = "🔴 Offline"
        
        st.markdown(f'''
        <div class="agent-card">
            {agent["icon"]} <strong>{agent["name"]}</strong><br>
            <small>{status}</small>
        </div>
        ''', unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 💬 Chat with XMRT Agents")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Eliza, your XMRT DAO assistant. Ask me about DAOs, governance, mining, or anything related to decentralized systems!", "agent": "Eliza"}
        ]
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'''<div class="user-message"><strong>You:</strong> {message["content"]}</div>''', unsafe_allow_html=True)
            else:
                agent_name = message.get("agent", "Assistant")
                st.markdown(f'''<div class="agent-message"><strong>🤖 {agent_name}:</strong> {message["content"]}</div>''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_agent, col_send = st.columns([3, 1, 1])
        
        with col_input:
            user_input = st.text_input("Ask anything...", placeholder="e.g., How does DAO voting work?")
        
        with col_agent:
            selected_agent = st.selectbox("Agent", ["Eliza", "DAO Agent", "Mining Agent", "Treasury Agent", "Governance Agent"])
        
        with col_send:
            st.markdown("<br>", unsafe_allow_html=True)
            send_button = st.form_submit_button("Send 🚀")
    
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Show thinking indicator
        with st.spinner(f"{selected_agent} is thinking..."):
            try:
                # Call the appropriate agent API
                api_url = "https://xmrtnet.onrender.com/api/eliza"
                
                response = requests.post(
                    api_url,
                    json={"message": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    agent_response = response.json().get("response", "I'm having trouble responding right now.")
                    source = response.json().get("source", "unknown")
                    
                    # Add agent response
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": agent_response,
                        "agent": selected_agent,
                        "source": source
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I'm experiencing technical difficulties. Please try again.",
                        "agent": selected_agent
                    })
                    
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Connection error: {str(e)}",
                    "agent": selected_agent
                })
        
        st.rerun()

with col2:
    st.markdown("## 📊 DAO Metrics")
    
    # Metrics cards
    metrics = [
        {"title": "Active Agents", "value": "5", "icon": "🤖"},
        {"title": "DAO Proposals", "value": "12", "icon": "📋"},
        {"title": "Mining Nodes", "value": "1,247", "icon": "⛏️"},
        {"title": "Treasury Balance", "value": "$2.4M", "icon": "💰"}
    ]
    
    for metric in metrics:
        st.markdown(f'''
        <div class="metric-card">
            <h2>{metric["icon"]}</h2>
            <h3>{metric["value"]}</h3>
            <p>{metric["title"]}</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("## 🎯 Quick Actions")
    
    if st.button("🗳️ View Proposals", use_container_width=True):
        st.info("Governance proposals coming soon!")
    
    if st.button("⛏️ Mining Status", use_container_width=True):
        st.info("Mining dashboard coming soon!")
    
    if st.button("💰 Treasury Info", use_container_width=True):
        st.info("Treasury analytics coming soon!")
    
    if st.button("📚 DAO Guide", use_container_width=True):
        st.info("Educational resources coming soon!")

# Footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌐 XMRT DAO - Building the Decentralized Future</p>
    <p><small>Powered by Autonomous AI Agents | Resilient Mining Network | Community Governance</small></p>
</div>
''', unsafe_allow_html=True)
