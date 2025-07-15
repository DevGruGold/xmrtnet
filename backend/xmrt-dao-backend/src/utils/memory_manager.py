import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import sessionmaker
from openai import OpenAI

from src.models.memory import db, ElizaMemory, ConversationHistory, MemoryAssociation, MemoryType, AssociationType


class MemoryManager:
    """
    Core memory management system for Eliza's long-term memory.
    Handles storage, retrieval, and management of memories with vector embeddings.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.openai_client = None
        self.embedding_model = 'text-embedding-ada-002'
        self.similarity_threshold = 0.7
        self.max_memories_per_user = 10000
        self.memory_retention_days = 365
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the memory manager with Flask app"""
        self.app = app
        
        # Initialize OpenAI client if API key is available
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        
        # Configuration from environment or defaults
        self.embedding_model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-ada-002')
        self.similarity_threshold = float(os.environ.get('SIMILARITY_THRESHOLD', '0.7'))
        self.max_memories_per_user = int(os.environ.get('MAX_MEMORIES_PER_USER', '10000'))
        self.memory_retention_days = int(os.environ.get('MEMORY_RETENTION_DAYS', '365'))
    
    def store_memory(self, user_id: str, content: str, memory_type: str = MemoryType.GENERAL,
                    session_id: str = None, metadata: Dict[str, Any] = None, 
                    tags: List[str] = None, relevance_score: float = 1.0) -> Optional[ElizaMemory]:
        """
        Store a new memory with optional vector embedding.
        
        Args:
            user_id: User identifier
            content: Memory content
            memory_type: Type of memory (factual, preference, etc.)
            session_id: Optional session identifier
            metadata: Additional metadata dictionary
            tags: List of tags for categorization
            relevance_score: Relevance score (0.0 to 1.0)
            
        Returns:
            ElizaMemory object if successful, None otherwise
        """
        try:
            # Create memory object
            memory = ElizaMemory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                session_id=session_id,
                metadata=metadata,
                tags=tags,
                relevance_score=relevance_score
            )
            
            # Generate embedding if OpenAI client is available
            if self.openai_client:
                try:
                    embedding = self._generate_embedding(content)
                    if embedding:
                        memory.embedding = np.array(embedding).tobytes()
                except Exception as e:
                    print(f"Warning: Failed to generate embedding: {e}")
            
            # Save to database
            db.session.add(memory)
            db.session.commit()
            
            # Check if user has too many memories and prune if necessary
            self._check_and_prune_memories(user_id)
            
            return memory
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            db.session.rollback()
            return None
    
    def retrieve_memories(self, user_id: str, query: str = None, memory_types: List[str] = None,
                         limit: int = 10, session_id: str = None, 
                         tags: List[str] = None) -> List[ElizaMemory]:
        """
        Retrieve memories based on various filters.
        
        Args:
            user_id: User identifier
            query: Text query for content search
            memory_types: List of memory types to filter by
            limit: Maximum number of memories to return
            session_id: Optional session filter
            tags: List of tags to filter by
            
        Returns:
            List of ElizaMemory objects
        """
        try:
            # Build query
            query_obj = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True
            )
            
            # Apply filters
            if memory_types:
                query_obj = query_obj.filter(ElizaMemory.memory_type.in_(memory_types))
            
            if session_id:
                query_obj = query_obj.filter(ElizaMemory.session_id == session_id)
            
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(ElizaMemory.tags.like(f'%{tag}%'))
                query_obj = query_obj.filter(or_(*tag_conditions))
            
            if query:
                query_obj = query_obj.filter(ElizaMemory.content.like(f'%{query}%'))
            
            # Order by relevance and recency
            query_obj = query_obj.order_by(
                desc(ElizaMemory.relevance_score),
                desc(ElizaMemory.created_at)
            )
            
            return query_obj.limit(limit).all()
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def search_memories_semantic(self, user_id: str, query_text: str, 
                               limit: int = 10, memory_types: List[str] = None) -> List[Tuple[ElizaMemory, float]]:
        """
        Search memories using semantic similarity with vector embeddings.
        
        Args:
            user_id: User identifier
            query_text: Text to search for semantically
            limit: Maximum number of memories to return
            memory_types: Optional list of memory types to filter by
            
        Returns:
            List of tuples (ElizaMemory, similarity_score)
        """
        if not self.openai_client:
            # Fallback to text search if embeddings not available
            memories = self.retrieve_memories(user_id, query_text, memory_types, limit)
            return [(memory, 1.0) for memory in memories]
        
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query_text)
            if not query_embedding:
                return []
            
            query_vector = np.array(query_embedding)
            
            # Get all memories with embeddings for the user
            query_obj = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True,
                ElizaMemory.embedding.isnot(None)
            )
            
            if memory_types:
                query_obj = query_obj.filter(ElizaMemory.memory_type.in_(memory_types))
            
            memories = query_obj.all()
            
            # Calculate similarities
            similarities = []
            for memory in memories:
                try:
                    memory_vector = np.frombuffer(memory.embedding, dtype=np.float32)
                    similarity = self._cosine_similarity(query_vector, memory_vector)
                    
                    if similarity >= self.similarity_threshold:
                        similarities.append((memory, similarity))
                except Exception as e:
                    print(f"Error calculating similarity for memory {memory.id}: {e}")
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def create_memory_association(self, source_id: int, target_id: int, 
                                association_type: str, strength: float = 1.0) -> Optional[MemoryAssociation]:
        """
        Create an association between two memories.
        
        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            association_type: Type of association
            strength: Association strength (0.0 to 1.0)
            
        Returns:
            MemoryAssociation object if successful, None otherwise
        """
        try:
            # Check if association already exists
            existing = MemoryAssociation.query.filter(
                MemoryAssociation.source_memory_id == source_id,
                MemoryAssociation.target_memory_id == target_id,
                MemoryAssociation.association_type == association_type
            ).first()
            
            if existing:
                # Update existing association strength
                existing.strength = max(existing.strength, strength)
                db.session.commit()
                return existing
            
            # Create new association
            association = MemoryAssociation(
                source_memory_id=source_id,
                target_memory_id=target_id,
                association_type=association_type,
                strength=strength
            )
            
            db.session.add(association)
            db.session.commit()
            
            return association
            
        except Exception as e:
            print(f"Error creating memory association: {e}")
            db.session.rollback()
            return None
    
    def get_memory_associations(self, memory_id: int, association_types: List[str] = None) -> List[MemoryAssociation]:
        """
        Get all associations for a specific memory.
        
        Args:
            memory_id: Memory ID to get associations for
            association_types: Optional list of association types to filter by
            
        Returns:
            List of MemoryAssociation objects
        """
        try:
            query_obj = MemoryAssociation.query.filter(
                or_(
                    MemoryAssociation.source_memory_id == memory_id,
                    MemoryAssociation.target_memory_id == memory_id
                )
            )
            
            if association_types:
                query_obj = query_obj.filter(MemoryAssociation.association_type.in_(association_types))
            
            return query_obj.all()
            
        except Exception as e:
            print(f"Error getting memory associations: {e}")
            return []
    
    def store_conversation(self, user_id: str, session_id: str, role: str, content: str,
                          message_type: str = None, autonomous_actions: List[Dict] = None,
                          context_data: Dict[str, Any] = None, memory_references: List[int] = None,
                          sentiment_score: float = None, importance_score: float = 0.5) -> Optional[ConversationHistory]:
        """
        Store a conversation entry in the history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            role: Role ('user' or 'assistant')
            content: Message content
            message_type: Optional message type
            autonomous_actions: List of autonomous actions taken
            context_data: Additional context data
            memory_references: List of memory IDs referenced
            sentiment_score: Sentiment analysis score
            importance_score: Importance score for the message
            
        Returns:
            ConversationHistory object if successful, None otherwise
        """
        try:
            conversation = ConversationHistory(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                message_type=message_type,
                autonomous_actions=autonomous_actions,
                context_data=context_data,
                memory_references=memory_references,
                sentiment_score=sentiment_score,
                importance_score=importance_score
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            return conversation
            
        except Exception as e:
            print(f"Error storing conversation: {e}")
            db.session.rollback()
            return None
    
    def get_conversation_history(self, user_id: str, session_id: str = None, 
                               limit: int = 50) -> List[ConversationHistory]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            session_id: Optional session filter
            limit: Maximum number of entries to return
            
        Returns:
            List of ConversationHistory objects
        """
        try:
            query_obj = ConversationHistory.query.filter(ConversationHistory.user_id == user_id)
            
            if session_id:
                query_obj = query_obj.filter(ConversationHistory.session_id == session_id)
            
            query_obj = query_obj.order_by(desc(ConversationHistory.timestamp))
            
            return query_obj.limit(limit).all()
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def prune_old_memories(self, user_id: str, days_threshold: int = None) -> int:
        """
        Remove old or low-relevance memories for a user.
        
        Args:
            user_id: User identifier
            days_threshold: Number of days to keep memories (default: retention_days)
            
        Returns:
            Number of memories pruned
        """
        if days_threshold is None:
            days_threshold = self.memory_retention_days
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
            
            # Find memories to prune (old and low relevance)
            memories_to_prune = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.created_at < cutoff_date,
                ElizaMemory.relevance_score < 0.3
            ).all()
            
            pruned_count = 0
            for memory in memories_to_prune:
                # Soft delete by setting is_active to False
                memory.is_active = False
                pruned_count += 1
            
            db.session.commit()
            return pruned_count
            
        except Exception as e:
            print(f"Error pruning memories: {e}")
            db.session.rollback()
            return 0
    
    def get_memory_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory usage analytics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with analytics data
        """
        try:
            # Total memories
            total_memories = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True
            ).count()
            
            # Memories by type
            memory_types = db.session.query(
                ElizaMemory.memory_type,
                func.count(ElizaMemory.id).label('count')
            ).filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True
            ).group_by(ElizaMemory.memory_type).all()
            
            # Recent activity (last 30 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=30)
            recent_memories = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True,
                ElizaMemory.created_at >= recent_cutoff
            ).count()
            
            # Conversation history count
            conversation_count = ConversationHistory.query.filter(
                ConversationHistory.user_id == user_id
            ).count()
            
            # Memory associations count
            association_count = db.session.query(MemoryAssociation).join(
                ElizaMemory, MemoryAssociation.source_memory_id == ElizaMemory.id
            ).filter(ElizaMemory.user_id == user_id).count()
            
            return {
                'total_memories': total_memories,
                'memory_types': {mt.memory_type: mt.count for mt in memory_types},
                'recent_memories_30d': recent_memories,
                'conversation_entries': conversation_count,
                'memory_associations': association_count,
                'max_memories_limit': self.max_memories_per_user,
                'retention_days': self.memory_retention_days
            }
            
        except Exception as e:
            print(f"Error getting memory analytics: {e}")
            return {}
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for text using OpenAI API"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def _check_and_prune_memories(self, user_id: str):
        """Check if user has too many memories and prune if necessary"""
        try:
            memory_count = ElizaMemory.query.filter(
                ElizaMemory.user_id == user_id,
                ElizaMemory.is_active == True
            ).count()
            
            if memory_count > self.max_memories_per_user:
                # Prune oldest, lowest relevance memories
                excess_count = memory_count - self.max_memories_per_user
                
                memories_to_prune = ElizaMemory.query.filter(
                    ElizaMemory.user_id == user_id,
                    ElizaMemory.is_active == True
                ).order_by(
                    ElizaMemory.relevance_score.asc(),
                    ElizaMemory.created_at.asc()
                ).limit(excess_count).all()
                
                for memory in memories_to_prune:
                    memory.is_active = False
                
                db.session.commit()
                
        except Exception as e:
            print(f"Error in auto-pruning: {e}")
            db.session.rollback()


# Global memory manager instance
memory_manager = MemoryManager()

