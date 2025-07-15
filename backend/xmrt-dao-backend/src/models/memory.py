from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from typing import Dict, Any, List, Optional

db = SQLAlchemy()

class ElizaMemory(db.Model):
    """
    Core memory storage for Eliza's long-term memory system.
    Stores individual memory entries with metadata and embeddings.
    """
    __tablename__ = 'eliza_memory'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    session_id = db.Column(db.String(255), nullable=True, index=True)
    memory_type = db.Column(db.String(50), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.Text, nullable=True)  # JSON string
    embedding = db.Column(db.LargeBinary, nullable=True)  # Vector embedding
    relevance_score = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.Column(db.Text, nullable=True)  # Comma-separated tags
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Relationships
    source_associations = db.relationship('MemoryAssociation', 
                                        foreign_keys='MemoryAssociation.source_memory_id',
                                        backref='source_memory', 
                                        cascade='all, delete-orphan')
    target_associations = db.relationship('MemoryAssociation', 
                                        foreign_keys='MemoryAssociation.target_memory_id',
                                        backref='target_memory', 
                                        cascade='all, delete-orphan')
    
    def __init__(self, user_id: str, content: str, memory_type: str = 'general', 
                 session_id: str = None, metadata: Dict[str, Any] = None, 
                 tags: List[str] = None, relevance_score: float = 1.0):
        self.user_id = user_id
        self.content = content
        self.memory_type = memory_type
        self.session_id = session_id
        self.metadata = json.dumps(metadata) if metadata else None
        self.tags = ','.join(tags) if tags else None
        self.relevance_score = relevance_score
    
    def get_metadata(self) -> Dict[str, Any]:
        """Parse and return metadata as dictionary"""
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set metadata from dictionary"""
        self.metadata = json.dumps(metadata) if metadata else None
    
    def get_tags(self) -> List[str]:
        """Parse and return tags as list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags: List[str]):
        """Set tags from list"""
        self.tags = ','.join(tags) if tags else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'memory_type': self.memory_type,
            'content': self.content,
            'metadata': self.get_metadata(),
            'relevance_score': self.relevance_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.get_tags(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<ElizaMemory {self.id}: {self.memory_type} for {self.user_id}>'


class ConversationHistory(db.Model):
    """
    Enhanced conversation history with persistent storage and memory references.
    Extends the current in-memory conversation history.
    """
    __tablename__ = 'conversation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, index=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=True)
    autonomous_actions = db.Column(db.Text, nullable=True)  # JSON string
    context_data = db.Column(db.Text, nullable=True)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    memory_references = db.Column(db.Text, nullable=True)  # Comma-separated memory IDs
    sentiment_score = db.Column(db.Float, nullable=True)
    importance_score = db.Column(db.Float, default=0.5)
    
    def __init__(self, user_id: str, session_id: str, role: str, content: str,
                 message_type: str = None, autonomous_actions: List[Dict] = None,
                 context_data: Dict[str, Any] = None, memory_references: List[int] = None,
                 sentiment_score: float = None, importance_score: float = 0.5):
        self.user_id = user_id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.message_type = message_type
        self.autonomous_actions = json.dumps(autonomous_actions) if autonomous_actions else None
        self.context_data = json.dumps(context_data) if context_data else None
        self.memory_references = ','.join(map(str, memory_references)) if memory_references else None
        self.sentiment_score = sentiment_score
        self.importance_score = importance_score
    
    def get_autonomous_actions(self) -> List[Dict[str, Any]]:
        """Parse and return autonomous actions as list"""
        if self.autonomous_actions:
            try:
                return json.loads(self.autonomous_actions)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_context_data(self) -> Dict[str, Any]:
        """Parse and return context data as dictionary"""
        if self.context_data:
            try:
                return json.loads(self.context_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def get_memory_references(self) -> List[int]:
        """Parse and return memory references as list of integers"""
        if self.memory_references:
            try:
                return [int(ref.strip()) for ref in self.memory_references.split(',') if ref.strip()]
            except ValueError:
                return []
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation entry to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'message_type': self.message_type,
            'autonomous_actions': self.get_autonomous_actions(),
            'context_data': self.get_context_data(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'memory_references': self.get_memory_references(),
            'sentiment_score': self.sentiment_score,
            'importance_score': self.importance_score
        }
    
    def __repr__(self):
        return f'<ConversationHistory {self.id}: {self.role} in {self.session_id}>'


class MemoryAssociation(db.Model):
    """
    Represents relationships between different memory entries.
    Enables Eliza to understand connections between concepts, users, and events.
    """
    __tablename__ = 'memory_associations'
    
    id = db.Column(db.Integer, primary_key=True)
    source_memory_id = db.Column(db.Integer, db.ForeignKey('eliza_memory.id'), nullable=False)
    target_memory_id = db.Column(db.Integer, db.ForeignKey('eliza_memory.id'), nullable=False)
    association_type = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, source_memory_id: int, target_memory_id: int, 
                 association_type: str, strength: float = 1.0):
        self.source_memory_id = source_memory_id
        self.target_memory_id = target_memory_id
        self.association_type = association_type
        self.strength = strength
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert association to dictionary representation"""
        return {
            'id': self.id,
            'source_memory_id': self.source_memory_id,
            'target_memory_id': self.target_memory_id,
            'association_type': self.association_type,
            'strength': self.strength,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<MemoryAssociation {self.id}: {self.source_memory_id} -> {self.target_memory_id}>'


# Memory type constants
class MemoryType:
    FACTUAL = 'factual'
    PREFERENCE = 'preference'
    CONTEXTUAL = 'contextual'
    PROCEDURAL = 'procedural'
    EMOTIONAL = 'emotional'
    TEMPORAL = 'temporal'
    GENERAL = 'general'


# Association type constants
class AssociationType:
    RELATED = 'related'
    CAUSAL = 'causal'
    TEMPORAL = 'temporal'
    PREFERENCE_RELATED = 'preference_related'
    CONTEXTUAL = 'contextual'
    CONTRADICTORY = 'contradictory'

