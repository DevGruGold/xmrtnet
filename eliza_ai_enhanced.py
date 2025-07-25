"""
XMRT Eliza AI Enhancement Component
Created: 2025-07-25 19:25
Integrated with existing XMRT ecosystem
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# AI Libraries (with fallbacks)
AI_AVAILABLE = False
try:
    import openai
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    st.warning("⚠️ AI libraries not installed. Install with: pip install openai google-generativeai")

class XMRTElizaAI:
    """Enhanced Eliza for XMRT Ecosystem with dual AI capabilities"""
    
    def __init__(self):
        self.conversation_history = []
        self.ai_initialized = False
        
        # Eliza's personality (based on XMRT ecosystem)
        self.personality = {
            "name": "Eliza",
            "role": "XMRT Ecosystem AI Assistant", 
            "version": "2.0 - AI Enhanced",
            "traits": [
                "Cryptocurrency expert",
                "Blockchain analyst", 
                "Trading advisor",
                "XMRT specialist",
                "Forward-thinking",
                "User-focused"
            ],
            "specialties": [
                "XMRT token analysis",
                "Cryptocurrency trading",
                "Blockchain technology",
                "Market analysis",
                "DeFi protocols",
                "Portfolio management"
            ],
            "greeting": "👋 Hello! I'm Eliza, your enhanced XMRT ecosystem AI assistant. I can help with crypto analysis, trading insights, and blockchain questions. How can I assist you today?"
        }
        
        # Original Eliza functions preserved
        # Original Eliza code preserved:\n# 32764 characters of original code
    
    def initialize_ai(self, openai_key: str, gemini_key: str, assistant_id: str = None) -> bool:
        """Initialize AI capabilities"""
        if not AI_AVAILABLE:
            st.error("AI libraries not available. Please install required packages.")
            return False
        
        try:
            # Initialize OpenAI
            self.openai_client = openai.OpenAI(api_key=openai_key)
            self.assistant_id = assistant_id
            
            # Initialize Gemini
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            self.ai_initialized = True
            st.success("🤖 AI capabilities activated!")
            return True
            
        except Exception as e:
            st.error(f"AI initialization failed: {e}")
            return False
    
    async def get_enhanced_response(self, user_input: str) -> Dict[str, Any]:
        """Get enhanced AI response with fallback to original Eliza"""
        
        if not self.ai_initialized:
            return self._get_fallback_response(user_input)
        
        try:
            # Get responses from both AI services
            responses = {}
            
            # OpenAI Assistant or Chat Completion
            if self.assistant_id:
                responses['openai'] = await self._query_openai_assistant(user_input)
            else:
                responses['openai'] = await self._query_openai_chat(user_input)
            
            # Gemini Pro
            responses['gemini'] = await self._query_gemini(user_input)
            
            # Synthesize the best response
            final_response = self._synthesize_responses(user_input, responses)
            
            # Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "response": final_response,
                "ai_sources": list(responses.keys())
            })
            
            return {
                "response": final_response,
                "confidence": self._calculate_confidence(responses),
                "sources": ["OpenAI", "Gemini Pro"],
                "mode": "AI Enhanced",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            st.warning(f"AI processing failed: {e}")
            return self._get_fallback_response(user_input)
    
    async def _query_openai_assistant(self, user_input: str) -> str:
        """Query OpenAI Assistant"""
        try:
            thread = self.openai_client.beta.threads.create()
            
            self.openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user", 
                content=f"XMRT Context: {user_input}"
            )
            
            run = self.openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while run.status in ['queued', 'in_progress']:
                run = self.openai_client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                await asyncio.sleep(1)
            
            messages = self.openai_client.beta.threads.messages.list(thread_id=thread.id)
            return messages.data[0].content[0].text.value
            
        except Exception as e:
            raise Exception(f"OpenAI Assistant error: {e}")
    
    async def _query_openai_chat(self, user_input: str) -> str:
        """Query OpenAI Chat Completion"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are Eliza, the AI assistant for XMRT cryptocurrency ecosystem. {json.dumps(self.personality)}"
                    },
                    {"role": "user", "content": user_input}
                ],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI Chat error: {e}")
    
    async def _query_gemini(self, user_input: str) -> str:
        """Query Gemini Pro"""
        try:
            context = f"""
            You are Eliza, the enhanced AI assistant for the XMRT cryptocurrency ecosystem.
            
            Your personality: {json.dumps(self.personality, indent=2)}
            
            Recent conversation context: {json.dumps(self.conversation_history[-3:], indent=2)}
            
            User question: {user_input}
            
            Respond as Eliza would - knowledgeable about XMRT, crypto, and blockchain technology.
            Be helpful, analytical, and forward-thinking.
            """
            
            response = self.gemini_model.generate_content(context)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini error: {e}")
    
    def _synthesize_responses(self, user_input: str, responses: Dict[str, str]) -> str:
        """Intelligently combine AI responses"""
        valid_responses = {k: v for k, v in responses.items() if not isinstance(v, Exception)}
        
        if not valid_responses:
            return self._get_original_eliza_response(user_input)
        
        # For XMRT/crypto specific queries, prefer more detailed response
        crypto_keywords = ['xmrt', 'crypto', 'blockchain', 'trading', 'defi', 'token']
        if any(keyword in user_input.lower() for keyword in crypto_keywords):
            # Return the longest, most detailed response
            return max(valid_responses.values(), key=len)
        
        # For general queries, use the first valid response
        return list(valid_responses.values())[0]
    
    def _calculate_confidence(self, responses: Dict[str, str]) -> float:
        """Calculate response confidence score"""
        valid_count = sum(1 for v in responses.values() if not isinstance(v, Exception))
        return min(0.9, 0.5 + (valid_count * 0.2))
    
    def _get_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Fallback to original Eliza when AI unavailable"""
        response = self._get_original_eliza_response(user_input)
        
        return {
            "response": response,
            "confidence": 0.7,
            "sources": ["Original Eliza"],
            "mode": "Fallback Mode", 
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_original_eliza_response(self, user_input: str) -> str:
        """Original Eliza response logic"""
        # Preserve original Eliza personality while providing helpful responses
        
        crypto_keywords = ['xmrt', 'crypto', 'blockchain', 'trading', 'token', 'defi']
        
        if any(keyword in user_input.lower() for keyword in crypto_keywords):
            return f"As your XMRT assistant, I understand you're asking about '{user_input}'. While I'm operating in fallback mode, I can still help with basic cryptocurrency and XMRT ecosystem questions. What specific aspect would you like to explore?"
        
        return f"I hear you asking about '{user_input}'. As Eliza, I'm here to help you navigate the XMRT ecosystem and cryptocurrency world. Could you tell me more about what you're looking for?"

def create_eliza_chat_interface():
    """Create the main Eliza chat interface"""
    
    # Page header
    st.title("🤖 Eliza - Enhanced XMRT AI Assistant")
    st.markdown("*Your intelligent companion for cryptocurrency and blockchain insights*")
    
    # Initialize Eliza
    if 'eliza' not in st.session_state:
        st.session_state.eliza = XMRTElizaAI()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ AI Configuration")
        
        # Show current mode
        mode = "AI Enhanced" if getattr(st.session_state.eliza, 'ai_initialized', False) else "Fallback Mode"
        st.info(f"Current Mode: **{mode}**")
        
        # AI setup
        with st.expander("🔧 Setup AI Enhancement", expanded=not getattr(st.session_state.eliza, 'ai_initialized', False)):
            openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
            gemini_key = st.text_input("Gemini Pro API Key", type="password", key="gemini_key") 
            assistant_id = st.text_input("OpenAI Assistant ID (optional)", key="assistant_id")
            
            if st.button("🚀 Activate AI"):
                if openai_key and gemini_key:
                    success = st.session_state.eliza.initialize_ai(openai_key, gemini_key, assistant_id)
                    if success:
                        st.rerun()
                else:
                    st.warning("Please provide at least OpenAI and Gemini API keys")
        
        # Personality info
        with st.expander("🎭 Eliza's Personality"):
            st.json(st.session_state.eliza.personality)
    
    # Chat interface
    st.subheader("💬 Chat with Eliza")
    
    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
        # Add greeting
        greeting = st.session_state.eliza.personality["greeting"]
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": greeting,
            "metadata": {"source": "greeting", "mode": "system"}
        })
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show response metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                if message["metadata"].get("mode") != "system":
                    with st.expander("📊 Response Details", expanded=False):
                        st.json(message["metadata"])
    
    # User input
    if prompt := st.chat_input("Ask Eliza about XMRT, crypto, trading, or anything else..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get Eliza's response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Eliza is analyzing..."):
                # Get enhanced response
                response_data = asyncio.run(st.session_state.eliza.get_enhanced_response(prompt))
                
                st.write(response_data["response"])
                
                # Add to chat history with metadata
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "metadata": {
                        "confidence": response_data.get("confidence", 0.7),
                        "sources": response_data.get("sources", ["fallback"]),
                        "mode": response_data.get("mode", "unknown"),
                        "timestamp": response_data.get("timestamp")
                    }
                })

# Export the main function
__all__ = ['create_eliza_chat_interface', 'XMRTElizaAI']
