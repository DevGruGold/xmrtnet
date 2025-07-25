"""
XMRT Enhanced Eliza AI Component with Streamlit Secrets Integration
Created/Updated: 2025-07-25 19:45
Fully integrated with XMRT ecosystem and automatic secrets management
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# AI Libraries with graceful fallback
AI_AVAILABLE = False
try:
    import openai
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    st.warning("⚠️ AI libraries not installed. Run: pip install openai google-generativeai")

class XMRTElizaAI:
    """Enhanced Eliza for XMRT Ecosystem with automatic secrets management"""
    
    def __init__(self):
        self.conversation_history = []
        self.ai_initialized = False
        self.secrets_loaded = False
        
        # Load secrets automatically
        self._load_secrets()
        
        # Eliza's enhanced personality
        self.personality = {
            "name": "Eliza",
            "role": "XMRT Ecosystem AI Assistant", 
            "version": "2.0 - AI Enhanced with Secrets",
            "traits": [
                "Cryptocurrency expert",
                "Blockchain analyst", 
                "Trading strategist",
                "XMRT specialist",
                "Market researcher",
                "DeFi consultant"
            ],
            "specialties": [
                "XMRT token analysis",
                "Cryptocurrency trading strategies",
                "Blockchain technology insights",
                "Market trend analysis",
                "DeFi protocol evaluation",
                "Portfolio optimization",
                "Risk management"
            ],
            "greeting": "🚀 Hello! I'm Enhanced Eliza, your XMRT ecosystem AI assistant powered by dual AI intelligence. I'm ready to help with crypto analysis, trading insights, blockchain questions, and everything XMRT. What would you like to explore today?"
        }
        
        # Auto-initialize AI if secrets are available
        if self.secrets_loaded and AI_AVAILABLE:
            self._auto_initialize_ai()
    
    def _load_secrets(self):
        """Load API keys from Streamlit secrets"""
        try:
            if hasattr(st, 'secrets') and 'eliza' in st.secrets:
                self.openai_key = st.secrets.eliza.get('openai_api_key')
                self.gemini_key = st.secrets.eliza.get('gemini_api_key')
                self.assistant_id = st.secrets.eliza.get('assistant_id')
                
                if self.openai_key and self.gemini_key:
                    self.secrets_loaded = True
                    print("✅ Secrets loaded successfully")
                else:
                    print("⚠️ Incomplete secrets configuration")
            else:
                print("⚠️ No secrets found - manual configuration required")
        except Exception as e:
            print(f"⚠️ Error loading secrets: {e}")
    
    def _auto_initialize_ai(self):
        """Automatically initialize AI with loaded secrets"""
        if not AI_AVAILABLE:
            return False
        
        try:
            # Initialize OpenAI
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
            # Initialize Gemini
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            self.ai_initialized = True
            print("🤖 AI auto-initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Auto-initialization failed: {e}")
            return False
    
    def manual_initialize_ai(self, openai_key: str, gemini_key: str, assistant_id: str = None) -> bool:
        """Manual AI initialization for fallback"""
        if not AI_AVAILABLE:
            st.error("AI libraries not available. Please install required packages.")
            return False
        
        try:
            self.openai_client = openai.OpenAI(api_key=openai_key)
            self.assistant_id = assistant_id
            
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            self.ai_initialized = True
            st.success("🤖 AI manually initialized!")
            return True
            
        except Exception as e:
            st.error(f"Manual initialization failed: {e}")
            return False
    
    async def get_enhanced_response(self, user_input: str) -> Dict[str, Any]:
        """Get enhanced AI response with comprehensive error handling"""
        
        if not self.ai_initialized:
            return self._get_fallback_response(user_input)
        
        try:
            # Parallel AI queries for speed
            responses = {}
            
            # OpenAI query (Assistant or Chat)
            if hasattr(self, 'assistant_id') and self.assistant_id:
                responses['openai'] = await self._query_openai_assistant(user_input)
            else:
                responses['openai'] = await self._query_openai_chat(user_input)
            
            # Gemini query
            responses['gemini'] = await self._query_gemini(user_input)
            
            # Intelligent response synthesis
            final_response = self._synthesize_responses(user_input, responses)
            
            # Update conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "response": final_response,
                "ai_sources": list(responses.keys()),
                "mode": "ai_enhanced"
            })
            
            return {
                "response": final_response,
                "confidence": self._calculate_confidence(responses),
                "sources": ["OpenAI", "Gemini Pro"],
                "mode": "AI Enhanced",
                "timestamp": datetime.now().isoformat(),
                "conversation_id": len(self.conversation_history)
            }
            
        except Exception as e:
            st.warning(f"AI processing error: {e}")
            return self._get_fallback_response(user_input)
    
    async def _query_openai_assistant(self, user_input: str) -> str:
        """Query OpenAI Assistant with XMRT context"""
        try:
            thread = self.openai_client.beta.threads.create()
            
            # Enhanced context for XMRT
            context_message = f"""
            XMRT Ecosystem Context:
            User Query: {user_input}
            
            Please respond as Eliza, the XMRT AI assistant, with focus on:
            - Cryptocurrency and blockchain insights
            - XMRT token specific information
            - Trading and market analysis
            - Technical accuracy with friendly tone
            """
            
            self.openai_client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user", 
                content=context_message
            )
            
            run = self.openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion with timeout
            max_wait = 30  # 30 second timeout
            wait_time = 0
            while run.status in ['queued', 'in_progress'] and wait_time < max_wait:
                run = self.openai_client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                await asyncio.sleep(1)
                wait_time += 1
            
            if run.status == 'completed':
                messages = self.openai_client.beta.threads.messages.list(thread_id=thread.id)
                return messages.data[0].content[0].text.value
            else:
                raise Exception(f"Assistant timeout or error: {run.status}")
            
        except Exception as e:
            raise Exception(f"OpenAI Assistant error: {e}")
    
    async def _query_openai_chat(self, user_input: str) -> str:
        """Query OpenAI Chat Completion with enhanced prompting"""
        try:
            system_prompt = f"""
            You are Eliza, the enhanced AI assistant for the XMRT cryptocurrency ecosystem.
            
            Your personality: {json.dumps(self.personality, indent=2)}
            
            Guidelines:
            - Provide accurate, helpful information about cryptocurrency and blockchain
            - Focus on XMRT ecosystem when relevant
            - Be analytical yet approachable
            - Include actionable insights when possible
            - Maintain professional but friendly tone
            
            Recent conversation context: {json.dumps(self.conversation_history[-3:], indent=2) if self.conversation_history else "No previous context"}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI Chat error: {e}")
    
    async def _query_gemini(self, user_input: str) -> str:
        """Query Gemini Pro with comprehensive context"""
        try:
            context = f"""
            You are Eliza, the enhanced AI assistant for the XMRT cryptocurrency ecosystem.
            
            Your role and personality: {json.dumps(self.personality, indent=2)}
            
            Current conversation context: {json.dumps(self.conversation_history[-5:], indent=2) if self.conversation_history else "Starting new conversation"}
            
            User question: {user_input}
            
            Instructions:
            - Respond as Eliza would - knowledgeable about XMRT, crypto, and blockchain
            - Provide detailed, actionable insights
            - Be analytical but maintain a helpful, forward-thinking tone
            - Include relevant market or technical analysis when appropriate
            - Focus on practical value for the user
            """
            
            response = self.gemini_model.generate_content(
                context,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 1000,
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini error: {e}")
    
    def _synthesize_responses(self, user_input: str, responses: Dict[str, str]) -> str:
        """Intelligently synthesize responses from multiple AI sources"""
        valid_responses = {k: v for k, v in responses.items() if not isinstance(v, Exception) and v}
        
        if not valid_responses:
            return self._get_original_eliza_response(user_input)
        
        # Analyze query type
        crypto_keywords = ['xmrt', 'crypto', 'blockchain', 'trading', 'defi', 'token', 'market', 'price']
        technical_keywords = ['how', 'what', 'explain', 'analyze', 'compare']
        
        is_crypto_query = any(keyword in user_input.lower() for keyword in crypto_keywords)
        is_technical_query = any(keyword in user_input.lower() for keyword in technical_keywords)
        
        if len(valid_responses) == 1:
            return list(valid_responses.values())[0]
        
        # For crypto/technical queries, prefer the more comprehensive response
        if is_crypto_query or is_technical_query:
            # Return the longest, most detailed response
            best_response = max(valid_responses.values(), key=len)
            return best_response
        
        # For general queries, use primary response
        return list(valid_responses.values())[0]
    
    def _calculate_confidence(self, responses: Dict[str, str]) -> float:
        """Calculate response confidence based on multiple factors"""
        valid_count = sum(1 for v in responses.values() if not isinstance(v, Exception) and v)
        
        if valid_count == 0:
            return 0.3
        elif valid_count == 1:
            return 0.7
        else:
            # Higher confidence when multiple sources agree
            return min(0.95, 0.6 + (valid_count * 0.15))
    
    def _get_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Enhanced fallback response when AI unavailable"""
        response = self._get_original_eliza_response(user_input)
        
        return {
            "response": response,
            "confidence": 0.6,
            "sources": ["Enhanced Fallback"],
            "mode": "Fallback Mode", 
            "timestamp": datetime.now().isoformat(),
            "note": "AI services unavailable - using enhanced fallback logic"
        }
    
    def _get_original_eliza_response(self, user_input: str) -> str:
        """Enhanced fallback logic with XMRT knowledge"""
        
        # Keyword-based response logic
        crypto_keywords = ['xmrt', 'crypto', 'cryptocurrency', 'blockchain', 'trading', 'token', 'defi']
        market_keywords = ['price', 'market', 'trend', 'analysis', 'forecast']
        help_keywords = ['help', 'how', 'what', 'explain', 'guide']
        
        user_lower = user_input.lower()
        
        if any(keyword in user_lower for keyword in crypto_keywords):
            return f"I understand you're asking about cryptocurrency and blockchain topics related to '{user_input}'. As your XMRT ecosystem assistant, I can help with trading strategies, market analysis, and blockchain insights. While I'm in fallback mode, I can still provide guidance based on fundamental crypto principles. What specific aspect would you like to explore further?"
        
        elif any(keyword in user_lower for keyword in market_keywords):
            return f"You're interested in market analysis for '{user_input}'. Market trends in cryptocurrency are influenced by multiple factors including adoption, technology developments, regulatory changes, and overall market sentiment. For XMRT specifically, I'd recommend monitoring ecosystem developments and community growth. What particular market aspect interests you most?"
        
        elif any(keyword in user_lower for keyword in help_keywords):
            return f"I'm here to help with '{user_input}'! As Enhanced Eliza, I specialize in cryptocurrency, blockchain technology, and the XMRT ecosystem. Even in fallback mode, I can provide guidance on trading concepts, blockchain fundamentals, and general crypto knowledge. What would you like to learn more about?"
        
        else:
            return f"Thank you for your question about '{user_input}'. As your XMRT AI assistant, I'm designed to help with cryptocurrency, blockchain, and trading topics. While I'm currently in fallback mode, I'm still here to assist. Could you tell me more about what specific information you're looking for?"

def create_eliza_chat_interface():
    """Create the comprehensive Eliza chat interface"""
    
    # Enhanced page header
    st.title("🤖 Enhanced Eliza - XMRT AI Assistant")
    st.markdown("*Powered by dual AI intelligence: OpenAI + Gemini Pro*")
    
    # Initialize Enhanced Eliza
    if 'eliza' not in st.session_state:
        st.session_state.eliza = XMRTElizaAI()
    
    # Status indicator
    ai_status = "🟢 AI Enhanced" if st.session_state.eliza.ai_initialized else "🟡 Fallback Mode"
    secrets_status = "🔐 Secrets Loaded" if st.session_state.eliza.secrets_loaded else "⚠️ Manual Config"
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Status: **{ai_status}**")
    with col2:
        st.info(f"Config: **{secrets_status}**")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Enhanced Eliza Control Panel")
        
        # AI Status
        with st.expander("📊 System Status", expanded=True):
            st.write(f"**AI Mode:** {ai_status}")
            st.write(f"**Configuration:** {secrets_status}")
            st.write(f"**Conversations:** {len(st.session_state.get('chat_messages', []))}")
            
            if st.session_state.eliza.ai_initialized:
                st.success("All systems operational! 🚀")
            else:
                st.warning("AI enhancement unavailable")
        
        # Manual configuration (if secrets not loaded)
        if not st.session_state.eliza.secrets_loaded:
            with st.expander("🔧 Manual AI Setup", expanded=True):
                st.warning("Secrets not found - manual configuration required")
                
                manual_openai = st.text_input("OpenAI API Key", type="password", key="manual_openai")
                manual_gemini = st.text_input("Gemini API Key", type="password", key="manual_gemini") 
                manual_assistant = st.text_input("Assistant ID (optional)", key="manual_assistant")
                
                if st.button("🚀 Initialize AI Manually"):
                    if manual_openai and manual_gemini:
                        success = st.session_state.eliza.manual_initialize_ai(
                            manual_openai, manual_gemini, manual_assistant
                        )
                        if success:
                            st.rerun()
                    else:
                        st.error("OpenAI and Gemini keys required")
        
        # Personality display
        with st.expander("🎭 Eliza's Personality"):
            st.json(st.session_state.eliza.personality)
        
        # Conversation controls
        with st.expander("💬 Conversation Controls"):
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_messages = []
                st.session_state.eliza.conversation_history = []
                st.success("Chat cleared!")
                st.rerun()
            
            if st.button("📥 Export Conversation"):
                if st.session_state.get('chat_messages'):
                    export_data = {
                        "export_time": datetime.now().isoformat(),
                        "conversation_count": len(st.session_state.chat_messages),
                        "messages": st.session_state.chat_messages
                    }
                    st.download_button(
                        "💾 Download JSON",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"eliza_conversation_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )
    
    # Main chat interface
    st.subheader("💬 Chat with Enhanced Eliza")
    
    # Initialize chat history with enhanced greeting
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
        greeting = st.session_state.eliza.personality["greeting"]
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": greeting,
            "metadata": {
                "source": "system_greeting", 
                "mode": ai_status,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    # Display chat history with enhanced formatting
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Enhanced metadata display for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                if metadata.get("source") != "system_greeting":
                    with st.expander("📊 Response Analytics", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            confidence = metadata.get("confidence", 0.5)
                            st.metric("Confidence", f"{confidence:.1%}")
                        
                        with col2:
                            sources = metadata.get("sources", ["unknown"])
                            st.metric("AI Sources", len(sources))
                        
                        with col3:
                            mode = metadata.get("mode", "unknown")
                            st.metric("Mode", mode)
                        
                        # Full metadata
                        st.json(metadata)
    
    # Enhanced user input with suggestions
    suggestion_prompts = [
        "What's the latest on XMRT token?",
        "Analyze current crypto market trends",
        "Explain DeFi yield farming strategies",
        "How do I evaluate blockchain projects?",
        "What are the risks in crypto trading?"
    ]
    
    # Quick suggestion buttons
    st.write("💡 **Quick Questions:**")
    cols = st.columns(len(suggestion_prompts))
    for i, prompt in enumerate(suggestion_prompts):
        with cols[i]:
            if st.button(f"{prompt[:20]}...", key=f"suggest_{i}"):
                # Trigger the prompt
                st.session_state.suggested_prompt = prompt
                st.rerun()
    
    # Handle suggested prompt
    if hasattr(st.session_state, 'suggested_prompt'):
        prompt = st.session_state.suggested_prompt
        del st.session_state.suggested_prompt
    else:
        prompt = st.chat_input("Ask Enhanced Eliza about XMRT, crypto, trading, or anything else...")
    
    # Process user input
    if prompt:
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get Enhanced Eliza's response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Enhanced Eliza is analyzing with dual AI intelligence..."):
                # Get enhanced response
                response_data = asyncio.run(st.session_state.eliza.get_enhanced_response(prompt))
                
                st.write(response_data["response"])
                
                # Add to chat history with full metadata
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "metadata": response_data
                })

def create_eliza_analytics_dashboard():
    """Create analytics dashboard for Enhanced Eliza"""
    st.header("📊 Enhanced Eliza Analytics Dashboard")
    
    if 'eliza' not in st.session_state:
        st.warning("Eliza not initialized")
        return
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ai_status = "Enhanced" if st.session_state.eliza.ai_initialized else "Fallback"
        st.metric("AI Mode", ai_status)
    
    with col2:
        conversation_count = len(st.session_state.get('chat_messages', []))
        st.metric("Total Messages", conversation_count)
    
    with col3:
        if st.session_state.eliza.conversation_history:
            avg_confidence = sum(
                conv.get('confidence', 0.5) 
                for conv in st.session_state.eliza.conversation_history[-10:]
            ) / min(10, len(st.session_state.eliza.conversation_history))
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        else:
            st.metric("Avg Confidence", "N/A")
    
    with col4:
        secrets_status = "Loaded" if st.session_state.eliza.secrets_loaded else "Manual"
        st.metric("Config Mode", secrets_status)
    
    # Conversation history analysis
    if st.session_state.eliza.conversation_history:
        st.subheader("📈 Conversation Analysis")
        
        # Recent conversations
        st.write("**Recent Conversations:**")
        for i, conv in enumerate(st.session_state.eliza.conversation_history[-5:]):
            with st.expander(f"Conversation {len(st.session_state.eliza.conversation_history) - 4 + i}: {conv['user_input'][:50]}..."):
                st.json(conv)
    else:
        st.info("No conversation data available yet. Start chatting with Eliza!")

# Export functions
__all__ = ['create_eliza_chat_interface', 'create_eliza_analytics_dashboard', 'XMRTElizaAI']
