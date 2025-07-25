#!/usr/bin/env python3
"""
ElizaOS Memory Integration with XMRT Langchain and Langflow
Integrates ElizaOS v1.2.9 with long-term memory capabilities using forked repositories
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass, asdict
import sqlite3
import pickle
import hashlib

# XMRT Langchain Memory Integration
try:
    from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
    from langchain.memory.chat_memory import BaseChatMemory
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.vectorstores import FAISS
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains import ConversationalRetrievalChain
    from langchain.llms import OpenAI
except ImportError:
    logging.warning("XMRT Langchain not installed. Install from: https://github.com/DevGruGold/xmrt-langchain-memory")

# XMRT Langflow Integration
try:
    from langflow import LangflowClient
    from langflow.graph import Graph
    from langflow.memory import MemoryStore
except ImportError:
    logging.warning("XMRT Langflow not installed. Install from: https://github.com/DevGruGold/xmrt-langflow-competition")

@dataclass
class MemoryContext:
    """Enhanced memory context for ElizaOS"""
    user_id: str
    session_id: str
    timestamp: datetime
    content: str
    context_type: str  # 'conversation', 'decision', 'action', 'learning'
    importance_score: float
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

class XMRTElizaMemoryManager:
    """
    Enhanced Memory Manager for ElizaOS v1.2.9 with XMRT Langchain and Langflow integration
    Provides long-term memory, context awareness, and learning capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('memory_db_path', 'data/eliza_memory.db')
        self.vector_store_path = config.get('vector_store_path', 'data/vector_store')
        self.max_memory_items = config.get('max_memory_items', 10000)
        self.memory_retention_days = config.get('memory_retention_days', 365)
        
        # Initialize components
        self._init_database()
        self._init_embeddings()
        self._init_langchain_memory()
        self._init_langflow_integration()
        
        # ElizaOS v1.2.9 compatibility
        self.eliza_version = "1.2.9"
        self.supported_features = [
            "action_chaining",
            "form_handling", 
            "code_quality_analysis",
            "enhanced_prompts",
            "improved_llm_selection"
        ]
        
        logging.info(f"XMRT Eliza Memory Manager initialized for ElizaOS v{self.eliza_version}")
    
    def _init_database(self):
        """Initialize SQLite database for persistent memory storage"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memory_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                content TEXT NOT NULL,
                context_type TEXT NOT NULL,
                importance_score REAL NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX(user_id),
                INDEX(session_id),
                INDEX(context_type),
                INDEX(importance_score)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                usage_count INTEGER DEFAULT 0,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def _init_embeddings(self):
        """Initialize OpenAI embeddings for semantic search"""
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                model="text-embedding-ada-002"
            )
            
            # Initialize or load vector store
            if os.path.exists(self.vector_store_path):
                self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings)
            else:
                # Create empty vector store
                sample_texts = ["Initial memory context"]
                self.vector_store = FAISS.from_texts(sample_texts, self.embeddings)
                self.vector_store.save_local(self.vector_store_path)
                
        except Exception as e:
            logging.error(f"Failed to initialize embeddings: {e}")
            self.embeddings = None
            self.vector_store = None
    
    def _init_langchain_memory(self):
        """Initialize XMRT Langchain memory components"""
        try:
            # Conversation buffer with window
            self.conversation_memory = ConversationBufferWindowMemory(
                k=20,  # Keep last 20 exchanges
                return_messages=True,
                memory_key="chat_history"
            )
            
            # Summary buffer for long-term context
            self.summary_memory = ConversationSummaryBufferMemory(
                llm=OpenAI(temperature=0),
                max_token_limit=2000,
                return_messages=True,
                memory_key="summary_history"
            )
            
            # Text splitter for processing long contexts
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            logging.info("XMRT Langchain memory components initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize Langchain memory: {e}")
            self.conversation_memory = None
            self.summary_memory = None
    
    def _init_langflow_integration(self):
        """Initialize XMRT Langflow for workflow management"""
        try:
            langflow_url = self.config.get('langflow_url', 'http://localhost:7860')
            self.langflow_client = LangflowClient(base_url=langflow_url)
            
            # Initialize memory workflows
            self.memory_workflows = {
                'context_analysis': 'xmrt-context-analysis-flow',
                'decision_making': 'xmrt-decision-flow',
                'learning_extraction': 'xmrt-learning-flow',
                'response_generation': 'xmrt-response-flow'
            }
            
            logging.info("XMRT Langflow integration initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize Langflow: {e}")
            self.langflow_client = None
    
    async def store_memory(self, context: MemoryContext) -> bool:
        """Store memory context with embeddings and metadata"""
        try:
            # Generate embedding if available
            embedding_blob = None
            if self.embeddings and context.content:
                embedding = await self._generate_embedding(context.content)
                context.embedding = embedding
                embedding_blob = pickle.dumps(embedding)
            
            # Store in database
            metadata_json = json.dumps(context.metadata or {})
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO memory_contexts 
                (user_id, session_id, timestamp, content, context_type, importance_score, embedding, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                context.user_id,
                context.session_id,
                context.timestamp,
                context.content,
                context.context_type,
                context.importance_score,
                embedding_blob,
                metadata_json
            ))
            
            self.conn.commit()
            
            # Add to vector store for semantic search
            if self.vector_store and context.embedding:
                self.vector_store.add_texts(
                    [context.content],
                    metadatas=[{
                        'user_id': context.user_id,
                        'session_id': context.session_id,
                        'context_type': context.context_type,
                        'importance_score': context.importance_score,
                        'timestamp': context.timestamp.isoformat()
                    }]
                )
                self.vector_store.save_local(self.vector_store_path)
            
            # Update Langchain memory
            if self.conversation_memory:
                if context.context_type == 'conversation':
                    if 'user_message' in context.metadata:
                        self.conversation_memory.chat_memory.add_user_message(context.metadata['user_message'])
                    if 'ai_response' in context.metadata:
                        self.conversation_memory.chat_memory.add_ai_message(context.metadata['ai_response'])
            
            logging.info(f"Memory stored: {context.context_type} for user {context.user_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to store memory: {e}")
            return False
    
    async def retrieve_relevant_memories(self, query: str, user_id: str, limit: int = 10) -> List[MemoryContext]:
        """Retrieve relevant memories using semantic search and filtering"""
        try:
            memories = []
            
            # Semantic search using vector store
            if self.vector_store:
                docs = self.vector_store.similarity_search(
                    query,
                    k=limit,
                    filter={'user_id': user_id} if user_id else None
                )
                
                for doc in docs:
                    # Reconstruct memory context from metadata
                    metadata = doc.metadata
                    memory = MemoryContext(
                        user_id=metadata.get('user_id', ''),
                        session_id=metadata.get('session_id', ''),
                        timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                        content=doc.page_content,
                        context_type=metadata.get('context_type', 'unknown'),
                        importance_score=metadata.get('importance_score', 0.5),
                        metadata=metadata
                    )
                    memories.append(memory)
            
            # Fallback to database search
            if not memories:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT user_id, session_id, timestamp, content, context_type, importance_score, metadata
                    FROM memory_contexts
                    WHERE user_id = ? AND content LIKE ?
                    ORDER BY importance_score DESC, timestamp DESC
                    LIMIT ?
                ''', (user_id, f'%{query}%', limit))
                
                for row in cursor.fetchall():
                    memory = MemoryContext(
                        user_id=row[0],
                        session_id=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        content=row[3],
                        context_type=row[4],
                        importance_score=row[5],
                        metadata=json.loads(row[6] or '{}')
                    )
                    memories.append(memory)
            
            return memories
            
        except Exception as e:
            logging.error(f"Failed to retrieve memories: {e}")
            return []
    
    async def generate_contextual_response(self, user_input: str, user_id: str, session_id: str) -> Dict[str, Any]:
        """Generate contextual response using memory and Langflow workflows"""
        try:
            # Retrieve relevant memories
            relevant_memories = await self.retrieve_relevant_memories(user_input, user_id, limit=5)
            
            # Build context from memories
            memory_context = []
            for memory in relevant_memories:
                memory_context.append({
                    'content': memory.content,
                    'type': memory.context_type,
                    'importance': memory.importance_score,
                    'timestamp': memory.timestamp.isoformat()
                })
            
            # Use Langflow for response generation if available
            if self.langflow_client:
                try:
                    flow_id = self.memory_workflows.get('response_generation')
                    if flow_id:
                        response = await self.langflow_client.run_flow(
                            flow_id=flow_id,
                            inputs={
                                'user_input': user_input,
                                'memory_context': memory_context,
                                'user_id': user_id,
                                'session_id': session_id
                            }
                        )
                        
                        if response and 'output' in response:
                            return {
                                'response': response['output'],
                                'context_used': memory_context,
                                'confidence': response.get('confidence', 0.8),
                                'method': 'langflow'
                            }
                except Exception as e:
                    logging.warning(f"Langflow response generation failed: {e}")
            
            # Fallback to Langchain conversation chain
            if self.conversation_memory and relevant_memories:
                context_text = "\n".join([m.content for m in relevant_memories[:3]])
                
                # Simple response generation with context
                response_text = f"Based on our previous conversations: {context_text}\n\nRegarding your question: {user_input}\n\nI understand the context and can help you with this."
                
                return {
                    'response': response_text,
                    'context_used': memory_context,
                    'confidence': 0.7,
                    'method': 'langchain_fallback'
                }
            
            # Basic response without memory
            return {
                'response': f"I understand you're asking about: {user_input}. How can I help you with this?",
                'context_used': [],
                'confidence': 0.5,
                'method': 'basic'
            }
            
        except Exception as e:
            logging.error(f"Failed to generate contextual response: {e}")
            return {
                'response': "I'm having trouble accessing my memory right now, but I'm here to help. Could you please rephrase your question?",
                'context_used': [],
                'confidence': 0.3,
                'method': 'error_fallback'
            }
    
    async def learn_from_interaction(self, user_input: str, ai_response: str, user_feedback: Optional[str] = None):
        """Learn from user interactions and improve responses"""
        try:
            # Extract learning patterns
            learning_data = {
                'user_input': user_input,
                'ai_response': ai_response,
                'user_feedback': user_feedback,
                'timestamp': datetime.now().isoformat(),
                'interaction_hash': hashlib.md5(f"{user_input}{ai_response}".encode()).hexdigest()
            }
            
            # Use Langflow for learning extraction if available
            if self.langflow_client:
                try:
                    flow_id = self.memory_workflows.get('learning_extraction')
                    if flow_id:
                        learning_result = await self.langflow_client.run_flow(
                            flow_id=flow_id,
                            inputs=learning_data
                        )
                        
                        if learning_result and 'patterns' in learning_result:
                            # Store learned patterns
                            for pattern in learning_result['patterns']:
                                await self._store_learning_pattern(
                                    pattern['type'],
                                    pattern['data'],
                                    pattern['confidence']
                                )
                except Exception as e:
                    logging.warning(f"Langflow learning extraction failed: {e}")
            
            # Store interaction as memory context
            interaction_context = MemoryContext(
                user_id=learning_data.get('user_id', 'system'),
                session_id=learning_data.get('session_id', 'learning'),
                timestamp=datetime.now(),
                content=f"User: {user_input}\nAI: {ai_response}",
                context_type='learning',
                importance_score=0.8 if user_feedback else 0.6,
                metadata=learning_data
            )
            
            await self.store_memory(interaction_context)
            
        except Exception as e:
            logging.error(f"Failed to learn from interaction: {e}")
    
    async def _store_learning_pattern(self, pattern_type: str, pattern_data: str, confidence: float):
        """Store learned patterns for future use"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO learning_patterns (pattern_type, pattern_data, confidence_score)
                VALUES (?, ?, ?)
            ''', (pattern_type, json.dumps(pattern_data), confidence))
            
            self.conn.commit()
            
        except Exception as e:
            logging.error(f"Failed to store learning pattern: {e}")
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI embeddings"""
        try:
            if self.embeddings:
                embedding = await asyncio.to_thread(self.embeddings.embed_query, text)
                return embedding
            return []
        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}")
            return []
    
    async def cleanup_old_memories(self):
        """Clean up old memories based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                DELETE FROM memory_contexts 
                WHERE timestamp < ? AND importance_score < 0.7
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            logging.info(f"Cleaned up {deleted_count} old memory contexts")
            
        except Exception as e:
            logging.error(f"Failed to cleanup old memories: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Total memories
            cursor.execute('SELECT COUNT(*) FROM memory_contexts')
            total_memories = cursor.fetchone()[0]
            
            # Memories by type
            cursor.execute('''
                SELECT context_type, COUNT(*) 
                FROM memory_contexts 
                GROUP BY context_type
            ''')
            memories_by_type = dict(cursor.fetchall())
            
            # Average importance score
            cursor.execute('SELECT AVG(importance_score) FROM memory_contexts')
            avg_importance = cursor.fetchone()[0] or 0
            
            # Learning patterns count
            cursor.execute('SELECT COUNT(*) FROM learning_patterns')
            learning_patterns_count = cursor.fetchone()[0]
            
            return {
                'total_memories': total_memories,
                'memories_by_type': memories_by_type,
                'average_importance': round(avg_importance, 3),
                'learning_patterns': learning_patterns_count,
                'eliza_version': self.eliza_version,
                'supported_features': self.supported_features,
                'vector_store_available': self.vector_store is not None,
                'langflow_available': self.langflow_client is not None
            }
            
        except Exception as e:
            logging.error(f"Failed to get memory stats: {e}")
            return {'error': str(e)}

# Example usage and integration
async def main():
    """Example usage of XMRT Eliza Memory Manager"""
    config = {
        'memory_db_path': 'data/eliza_memory.db',
        'vector_store_path': 'data/vector_store',
        'langflow_url': 'http://localhost:7860',
        'max_memory_items': 10000,
        'memory_retention_days': 365
    }
    
    memory_manager = XMRTElizaMemoryManager(config)
    
    # Example interaction
    user_id = "user123"
    session_id = "session456"
    
    # Store a memory
    context = MemoryContext(
        user_id=user_id,
        session_id=session_id,
        timestamp=datetime.now(),
        content="User asked about XMRT staking rewards",
        context_type="conversation",
        importance_score=0.8,
        metadata={"topic": "staking", "sentiment": "curious"}
    )
    
    await memory_manager.store_memory(context)
    
    # Generate contextual response
    response = await memory_manager.generate_contextual_response(
        "What are the current staking rewards?",
        user_id,
        session_id
    )
    
    print(f"Response: {response['response']}")
    print(f"Context used: {len(response['context_used'])} memories")
    print(f"Confidence: {response['confidence']}")
    
    # Learn from interaction
    await memory_manager.learn_from_interaction(
        "What are the current staking rewards?",
        response['response'],
        "helpful"
    )
    
    # Get stats
    stats = memory_manager.get_memory_stats()
    print(f"Memory stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())

