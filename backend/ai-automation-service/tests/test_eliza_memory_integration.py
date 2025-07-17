import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import os

from src.eliza_memory_integration import XMRTElizaMemoryManager, MemoryContext
from src.autonomous_eliza import AutonomousElizaOS, AutonomousAction, AgentCapability, DecisionLevel

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "SUPABASE_URL": "https://mock.supabase.co",
        "SUPABASE_KEY": "mock_key",
        "OPENAI_API_KEY": "mock_openai_key"
    }):
        yield

@pytest.fixture
def mock_supabase_client():
    mock_client = MagicMock()
    
    # Mock for insert operation
    mock_client.table.return_value.insert.return_value.execute.return_value = AsyncMock(return_value=MagicMock(data=[{}], count=1))
    
    # Mock for select operations in retrieve_relevant_memories
    mock_client.table.return_value.select.return_value.eq.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value = AsyncMock(return_value=MagicMock(data=[
        {
            "user_id": "test_user",
            "session_id": "test_session",
            "timestamp": datetime.now().isoformat(),
            "content": "Retrieved content",
            "context_type": "conversation",
            "importance_score": 0.6,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"retrieved": True},
        }
    ]))
    
    # Mock for delete operation
    mock_client.table.return_value.delete.return_value.lt.return_value.lt.return_value.execute.return_value = AsyncMock(return_value=MagicMock(data=[{}], count=1))
    
    # Mock for get_memory_stats
    mock_select_execute_side_effect = [
        MagicMock(data=[{"count": 10}]),  # total_memories_response
        MagicMock(data=[{"context_type": "conversation", "count": 5}, {"context_type": "learning", "count": 5}]),  # memories_by_type_response
        MagicMock(data=[{"avg": 0.75}]),  # avg_importance_response
        MagicMock(data=[{"count": 2}]),  # learning_patterns_count_response
    ]
    
    # Create a mock for the chain of calls leading to execute() for select operations
    mock_select_chain = MagicMock()
    mock_select_chain.select.return_value = mock_select_chain
    mock_select_chain.eq.return_value = mock_select_chain
    mock_select_chain.ilike.return_value = mock_select_chain
    mock_select_chain.order.return_value = mock_select_chain
    mock_select_chain.limit.return_value = mock_select_chain
    mock_select_chain.group_by.return_value = mock_select_chain
    
    # Assign the side_effect to the execute method of the select chain
    mock_select_chain.execute.side_effect = [AsyncMock(return_value=item) for item in mock_select_execute_side_effect]
    
    # Ensure table().select() returns this mock chain
    mock_client.table.return_value.select.return_value = mock_select_chain

    return mock_client

@pytest.fixture
def memory_manager(mock_supabase_client):
    with patch("src.eliza_memory_integration.create_client", return_value=mock_supabase_client):
        manager = XMRTElizaMemoryManager(config={
            "vector_store_path": "data/vector_store",
            "max_memory_items": 10000,
            "memory_retention_days": 365,
        })
        # Mock embeddings and vector_store if they are not properly initialized
        manager.embeddings = MagicMock()
        manager.vector_store = MagicMock()
        manager.vector_store.save_local = MagicMock()
        manager.vector_store.from_texts = MagicMock(return_value=MagicMock())
        manager.embeddings.embed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return manager

@pytest.mark.asyncio
async def test_store_memory_supabase(memory_manager):
    context = MemoryContext(
        user_id="test_user",
        session_id="test_session",
        timestamp=datetime.now(),
        content="Test content",
        context_type="conversation",
        importance_score=0.5,
        metadata={"key": "value"},
    )
    result = await memory_manager.store_memory(context)
    assert result is True
    memory_manager.supabase_client.table.assert_called_with("memory_contexts")
    memory_manager.supabase_client.table.return_value.insert.assert_called_once()

@pytest.mark.asyncio
async def test_retrieve_relevant_memories_supabase(memory_manager):
    memories = await memory_manager.retrieve_relevant_memories("query", "test_user")
    assert len(memories) == 1
    assert memories[0].content == "Retrieved content"

@pytest.mark.asyncio
async def test_generate_contextual_response(memory_manager):
    memory_manager.retrieve_relevant_memories = AsyncMock(return_value=[
        MemoryContext(
            user_id="test_user",
            session_id="test_session",
            timestamp=datetime.now(),
            content="Previous conversation point",
            context_type="conversation",
            importance_score=0.7,
            metadata={},
        )
    ])
    response = await memory_manager.generate_contextual_response("New query", "test_user", "test_session")
    assert "Based on our previous conversations" in response["response"]
    assert response["method"] == "langchain_fallback"

@pytest.mark.asyncio
async def test_learn_from_interaction_supabase(memory_manager):
    memory_manager.store_memory = AsyncMock(return_value=True)
    await memory_manager.learn_from_interaction("user_input", "ai_response", "helpful")
    memory_manager.store_memory.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup_old_memories_supabase(memory_manager):
    memory_manager.supabase_client.table.return_value.delete.return_value.lt.return_value.lt.return_value.execute.return_value = AsyncMock(return_value=MagicMock(data=[{}], count=5))
    await memory_manager.cleanup_old_memories()
    memory_manager.supabase_client.table.return_value.delete.assert_called_once()

@pytest.mark.asyncio
async def test_get_memory_stats_supabase(memory_manager):
    stats = await memory_manager.get_memory_stats()
    assert stats["total_memories"] == 10
    assert stats["memories_by_type"] == {"conversation": 5, "learning": 5}
    assert stats["average_importance"] == 0.75
    assert stats["learning_patterns"] == 2
    assert stats["vector_store_available"] is True
    assert stats["supabase_available"] is True

@pytest.mark.asyncio
async def test_init_embeddings_no_openai_key(mock_supabase_client):
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        manager = XMRTElizaMemoryManager(config={
            "vector_store_path": "data/vector_store",
            "max_memory_items": 10000,
            "memory_retention_days": 365,
        })
        assert manager.embeddings is None
        assert manager.vector_store is None

@pytest.mark.asyncio
async def test_init_langchain_memory_no_langchain_installed(mock_supabase_client):
    with patch("src.eliza_memory_integration.ConversationBufferWindowMemory", side_effect=ImportError):
        manager = XMRTElizaMemoryManager(config={
            "vector_store_path": "data/vector_store",
            "max_memory_items": 10000,
            "memory_retention_days": 365,
        })
        assert manager.conversation_memory is None
        assert manager.summary_memory is None



