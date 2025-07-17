#!/usr/bin/env python3
"""
ElizaOS Memory Integration with XMRT Langchain and Supabase
Integrates ElizaOS with long-term memory capabilities using Langchain and Supabase
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

# Supabase Integration
from supabase import Client, create_client

# Langchain Memory Integration
try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain_openai import OpenAIEmbeddings, OpenAI # Updated import
    from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
    from langchain.schema import AIMessage, BaseMessage, HumanMessage
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS # Updated import
except ImportError:
    logging.warning("Langchain not installed or missing components. Please install langchain.")


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
    Enhanced Memory Manager for ElizaOS with Langchain and Supabase integration
    Provides long-term memory, context awareness, and learning capabilities
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.vector_store_path = config.get("vector_store_path", "data/vector_store")
        self.max_memory_items = config.get("max_memory_items", 10000)
        self.memory_retention_days = config.get("memory_retention_days", 365)

        # Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_client: Optional[Client] = None

        # Initialize components
        self._init_supabase_client()
        self._init_embeddings()
        self._init_langchain_memory()

        logging.info("XMRT Eliza Memory Manager initialized")

    def _init_supabase_client(self):
        """Initialize Supabase client"""
        if self.supabase_url and self.supabase_key:
            try:
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                logging.info("Supabase client initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Supabase client: {e}")
        else:
            logging.warning("Supabase URL or Key not found in environment variables. Supabase integration will be skipped.")

    def _init_embeddings(self):
        """Initialize OpenAI embeddings for semantic search"""
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-ada-002"
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
        """Initialize Langchain memory components"""
        try:
            # Conversation buffer with window
            self.conversation_memory = ConversationBufferWindowMemory(
                k=20,  # Keep last 20 exchanges
                return_messages=True,
                memory_key="chat_history",
            )

            # Summary buffer for long-term context
            self.summary_memory = ConversationSummaryBufferMemory(
                llm=OpenAI(temperature=0),
                max_token_limit=2000,
                return_messages=True,
                memory_key="summary_history",
            )

            # Text splitter for processing long contexts
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            logging.info("Langchain memory components initialized")

        except Exception as e:
            logging.error(f"Failed to initialize Langchain memory: {e}")
            self.conversation_memory = None
            self.summary_memory = None

    async def store_memory(self, context: MemoryContext) -> bool:
        """Store memory context with embeddings and metadata in Supabase"""
        try:
            if not self.supabase_client:
                logging.warning("Supabase client not initialized. Cannot store memory.")
                return False

            # Generate embedding if available
            if self.embeddings and context.content:
                embedding = await self._generate_embedding(context.content)
                context.embedding = embedding

            # Store in Supabase
            data, count = (
                await self.supabase_client.table("memory_contexts")
                .insert(
                    {
                        "user_id": context.user_id,
                        "session_id": context.session_id,
                        "timestamp": context.timestamp.isoformat(),
                        "content": context.content,
                        "context_type": context.context_type,
                        "importance_score": context.importance_score,
                        "embedding": list(context.embedding) if context.embedding else None,  # Supabase can store float arrays
                        "metadata": context.metadata,
                    }
                )
                .execute()
            )
            logging.info(f"Memory stored in Supabase: {context.context_type} for user {context.user_id}")
            return True

        except Exception as e:
            logging.error(f"Failed to store memory in Supabase: {e}")
            return False

    async def retrieve_relevant_memories(self, query: str, user_id: str, limit: int = 10) -> List[MemoryContext]:
        """Retrieve relevant memories using semantic search and filtering from Supabase"""
        try:
            if not self.supabase_client:
                logging.warning("Supabase client not initialized. Cannot retrieve memories.")
                return []

            memories = []

            # Retrieve from Supabase
            response = (
                await self.supabase_client.table("memory_contexts")
                .select("*")
                .eq("user_id", user_id)
                .ilike("content", f"%{query}%")
                .order("importance_score", desc=True)
                .limit(limit)
                .execute()
            )

            for row in response.data:
                memory = MemoryContext(
                    user_id=row["user_id"],
                    session_id=row["session_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    content=row["content"],
                    context_type=row["context_type"],
                    importance_score=row["importance_score"],
                    embedding=row["embedding"],
                    metadata=row["metadata"],
                )
                memories.append(memory)

            return memories

        except Exception as e:
            logging.error(f"Failed to retrieve memories from Supabase: {e}")
            return []

    async def generate_contextual_response(
        self, user_input: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Generate contextual response using memory and Langchain"""
        try:
            # Retrieve relevant memories
            relevant_memories = await self.retrieve_relevant_memories(user_input, user_id, limit=5)

            # Build context from memories
            memory_context = []
            for memory in relevant_memories:
                memory_context.append(
                    {
                        "content": memory.content,
                        "type": memory.context_type,
                        "importance": memory.importance_score,
                        "timestamp": memory.timestamp.isoformat(),
                    }
                )

            # Fallback to Langchain conversation chain
            if self.conversation_memory and relevant_memories:
                context_text = "\n".join([m.content for m in relevant_memories[:3]])

                # Simple response generation with context
                response_text = f"Based on our previous conversations: {context_text}\n\nRegarding your question: {user_input}\n\nI understand the context and can help you with this."

                return {
                    "response": response_text,
                    "context_used": memory_context,
                    "confidence": 0.7,
                    "method": "langchain_fallback",
                }

            # Basic response without memory
            return {
                "response": f"I understand you're asking about: {user_input}. How can I help you with this?",
                "context_used": [],
                "confidence": 0.5,
                "method": "basic",
            }

        except Exception as e:
            logging.error(f"Failed to generate contextual response: {e}")
            return {
                "response": "I'm having trouble accessing my memory right now, but I'm here to help. Could you please rephrase your question?",
                "context_used": [],
                "confidence": 0.3,
                "method": "error_fallback",
            }

    async def learn_from_interaction(
        self, user_input: str, ai_response: str, user_feedback: Optional[str] = None
    ):
        """Learn from user interactions and improve responses"""
        try:
            # Extract learning patterns
            learning_data = {
                "user_input": user_input,
                "ai_response": ai_response,
                "user_feedback": user_feedback,
                "timestamp": datetime.now().isoformat(),
                "interaction_hash": hashlib.md5(f"{user_input}{ai_response}".encode()).hexdigest(),
            }

            # Store interaction as memory context
            interaction_context = MemoryContext(
                user_id=learning_data.get("user_id", "system"),
                session_id=learning_data.get("session_id", "learning"),
                timestamp=datetime.now(),
                content=f"User: {user_input}\nAI: {ai_response}",
                context_type="learning",
                importance_score=0.8 if user_feedback else 0.6,
                metadata=learning_data,
            )

            await self.store_memory(interaction_context)

        except Exception as e:
            logging.error(f"Failed to learn from interaction: {e}")

    async def _store_learning_pattern(self, pattern_type: str, pattern_data: str, confidence: float):
        """Store learned patterns for future use in Supabase"""
        try:
            if not self.supabase_client:
                logging.warning("Supabase client not initialized. Cannot store learning pattern.")
                return

            # Store in Supabase
            data, count = (
                await self.supabase_client.table("learning_patterns")
                .insert(
                    {
                        "pattern_type": pattern_type,
                        "pattern_data": pattern_data,
                        "confidence_score": confidence,
                    }
                )
                .execute()
            )
            logging.info(f"Learning pattern stored in Supabase: {pattern_type}")

        except Exception as e:
            logging.error(f"Failed to store learning pattern in Supabase: {e}")

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
        """Clean up old memories based on retention policy in Supabase"""
        try:
            if not self.supabase_client:
                logging.warning("Supabase client not initialized. Cannot clean up memories.")
                return

            cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)

            # Clean up in Supabase
            data, count = (
                await self.supabase_client.table("memory_contexts")
                .delete()
                .lt("timestamp", cutoff_date.isoformat())
                .lt("importance_score", 0.7)
                .execute()
            )
            deleted_count = count
            logging.info(f"Cleaned up {deleted_count} old memory contexts in Supabase")

        except Exception as e:
            logging.error(f"Failed to cleanup old memories in Supabase: {e}")

    async def get_memory_stats(self) -> Dict[str, Any]: # Changed to async
        """Get memory system statistics from Supabase"""
        try:
            if not self.supabase_client:
                logging.warning("Supabase client not initialized. Cannot get memory stats.")
                return {"error": "Supabase client not initialized"}

            # Get stats from Supabase
            total_memories_response = (
                await self.supabase_client.table("memory_contexts").select("count").execute() # Added await
            )
            total_memories = total_memories_response.data[0]["count"]

            memories_by_type_response = (
                await self.supabase_client.table("memory_contexts") # Added await
                .select("context_type", "count")
                .group_by("context_type")
                .execute()
            )
            memories_by_type = {
                row["context_type"]: row["count"] for row in memories_by_type_response.data
            }

            avg_importance_response = (
                await self.supabase_client.table("memory_contexts") # Added await
                .select("avg:importance_score")
                .execute()
            )
            avg_importance = avg_importance_response.data[0]["avg"] or 0

            learning_patterns_count_response = (
                await self.supabase_client.table("learning_patterns").select("count").execute() # Added await
            )
            learning_patterns_count = learning_patterns_count_response.data[0]["count"]

            return {
                "total_memories": total_memories,
                "memories_by_type": memories_by_type,
                "average_importance": round(avg_importance, 3),
                "learning_patterns": learning_patterns_count,
                "vector_store_available": self.vector_store is not None,
                "supabase_available": self.supabase_client is not None,
            }

        except Exception as e:
            logging.error(f"Failed to get memory stats from Supabase: {e}")
            return {"error": str(e)}


# Example usage and integration
async def main():
    """Example usage of XMRT Eliza Memory Manager"""
    config = {
        "vector_store_path": "data/vector_store",
        "max_memory_items": 10000,
        "memory_retention_days": 365,
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
        metadata={"topic": "staking", "sentiment": "curious"},
    )

    await memory_manager.store_memory(context)

    # Generate contextual response
    response = await memory_manager.generate_contextual_response(
        "What are the current staking rewards?", user_id, session_id
    )

    print(f"Response: {response['response']}")
    print(f"Context used: {len(response['context_used'])} memories")
    print(f"Confidence: {response['confidence']}")

    # Learn from interaction
    await memory_manager.learn_from_interaction(
        "What are the current staking rewards?", response["response"], "helpful"
    )

    # Get stats
    stats = await memory_manager.get_memory_stats() # Added await
    print(f"Memory stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())





