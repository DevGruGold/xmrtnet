import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure page
st.set_page_config(
    page_title="XMRT DAO",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-First CSS
st.markdown('''
<style>
    /* Hide Streamlit default elements for cleaner mobile look */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stDecoration {display:none;}
    
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Beautiful header - mobile optimized */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%);
        padding: 1.5rem 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 1.8rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header h3 {
        font-size: 1rem;
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    
    .main-header p {
        font-size: 0.85rem;
        margin: 0;
        opacity: 0.8;
    }
    
    /* Chat container - perfect for mobile */
    .chat-container {
        background: #f8f9fa;
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Message bubbles - mobile optimized */
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 5px 18px;
        margin: 0.5rem 0;
        max-width: 85%;
        margin-left: auto;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        word-wrap: break-word;
    }
    
    .agent-message {
        background: white;
        color: #333;
        padding: 0.75rem 1rem;
        border-radius: 18px 18px 18px 5px;
        margin: 0.5rem 0;
        max-width: 85%;
        border-left: 4px solid #28a745;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    /* Agent status cards - mobile friendly */
    .agent-card {
        background: white;
        border-radius: 12px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
        font-size: 0.85rem;
    }
    
    /* Metrics cards - mobile grid */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-top: 3px solid #667eea;
    }
    
    .metric-card h2 {
        font-size: 1.5rem;
        margin: 0;
    }
    
    .metric-card h3 {
        font-size: 1.2rem;
        margin: 0.5rem 0;
        color: #667eea;
    }
    
    .metric-card p {
        font-size: 0.8rem;
        margin: 0;
        color: #666;
    }
    
    /* Mobile input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        font-size: 0.9rem;
    }
    
    /* Sidebar styling for mobile */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Form styling */
    .stForm {
        border: none;
        padding: 0;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 15px;
        border: 2px solid #e9ecef;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0.5rem;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header h3 {
            font-size: 0.9rem;
        }
        
        .chat-container {
            margin: 0.5rem 0;
            padding: 0.75rem;
        }
        
        .user-message, .agent-message {
            max-width: 90%;
            font-size: 0.85rem;
            padding: 0.6rem 0.8rem;
        }
        
        .metric-card {
            padding: 0.75rem;
        }
    }
    
    /* Loading spinner */
    .stSpinner {
        text-align: center;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #666;
        padding: 1rem;
        font-size: 0.8rem;
        border-top: 1px solid #e9ecef;
        margin-top: 2rem;
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

# Mobile-optimized layout
if st.sidebar.button("📊 Show Agent Status"):
    with st.sidebar:
        st.markdown("### 🤖 Agent Status")
        
        agents = [
            {"name": "Eliza", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🧠"},
            {"name": "DAO Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🏛️"},
            {"name": "Mining Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "⛏️"},
            {"name": "Treasury Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "💰"},
            {"name": "Governance Agent", "endpoint": "https://xmrtnet.onrender.com/api/eliza/health", "icon": "🗳️"}
        ]
        
        for agent in agents:
            try:
                response = requests.get(agent["endpoint"], timeout=3)
                status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
            except:
                status = "🔴 Offline"
            
            st.markdown(f'''
            <div class="agent-card">
                {agent["icon"]} <strong>{agent["name"]}</strong><br>
                <small>{status}</small>
            </div>
            ''', unsafe_allow_html=True)

# Main chat interface
st.markdown("## 💬 Chat with XMRT Agents")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Eliza, your XMRT DAO assistant. Ask me about DAOs, governance, mining, or decentralized systems!", "agent": "Eliza"}
    ]

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'''<div class="user-message"><strong>You:</strong> {message["content"]}</div>''', unsafe_allow_html=True)
    else:
        agent_name = message.get("agent", "Assistant")
        st.markdown(f'''<div class="agent-message"><strong>🤖 {agent_name}:</strong> {message["content"]}</div>''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Mobile-optimized input form
with st.form("chat_form", clear_on_submit=True):
    # Stack inputs vertically on mobile
    user_input = st.text_input("💬 Ask anything...", placeholder="e.g., How does DAO voting work?")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_agent = st.selectbox("🤖 Choose Agent", ["Eliza", "DAO Agent", "Mining Agent", "Treasury Agent", "Governance Agent"])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.form_submit_button("Send 🚀", use_container_width=True)

if send_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show thinking indicator
    with st.spinner(f"🤔 {selected_agent} is thinking..."):
        try:
            response = requests.post(
                "https://xmrtnet.onrender.com/api/eliza",
                json={"message": user_input},
                timeout=30
            )
            
            if response.status_code == 200:
                agent_response = response.json().get("response", "I'm having trouble responding right now.")
                source = response.json().get("source", "unknown")
                
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
                "content": f"Connection error. Please check your internet and try again.",
                "agent": selected_agent
            })
    
    st.rerun()

# Mobile metrics section
if st.button("📊 Show DAO Metrics", use_container_width=True):
    st.markdown("### 📈 DAO Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="metric-card">
            <h2>🤖</h2>
            <h3>5</h3>
            <p>Active Agents</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="metric-card">
            <h2>⛏️</h2>
            <h3>1,247</h3>
            <p>Mining Nodes</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <h2>📋</h2>
            <h3>12</h3>
            <p>DAO Proposals</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="metric-card">
            <h2>💰</h2>
            <h3>$2.4M</h3>
            <p>Treasury Balance</p>
        </div>
        ''', unsafe_allow_html=True)

# Quick actions
st.markdown("### 🎯 Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("🗳️ View Proposals", use_container_width=True):
        st.info("🚀 Governance proposals coming soon!")
    
    if st.button("💰 Treasury Info", use_container_width=True):
        st.info("📊 Treasury analytics coming soon!")

with col2:
    if st.button("⛏️ Mining Status", use_container_width=True):
        st.info("⚡ Mining dashboard coming soon!")
    
    if st.button("📚 DAO Guide", use_container_width=True):
        st.info("📖 Educational resources coming soon!")

# Footer
st.markdown('''
<div class="footer">
    <p>🌐 <strong>XMRT DAO</strong> - Building the Decentralized Future</p>
    <p>Powered by Autonomous AI Agents • Resilient Mining Network • Community Governance</p>
</div>
''', unsafe_allow_html=True)
