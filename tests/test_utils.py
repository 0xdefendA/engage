import pytest
from unittest.mock import Mock, patch
from engage.utils import get_agent
from agno.models.base import Model
from agno.agent import Agent, AgentMemory
from agno.memory.classifier import MemoryClassifier
from agno.memory.summarizer import MemorySummarizer
from agno.memory.manager import MemoryManager
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.memory.db.sqlite import SqliteMemoryDb

@pytest.fixture
def mock_config():
    return {
        "model": {
            "provider": "google",
            "model_name": "gemini-1.5-flash"
        }
    }

@pytest.fixture
def mock_model():
    return Mock(spec=Model)

@patch("engage.utils.get_model")
def test_get_agent_creates_agent_with_correct_config(mock_get_model, mock_config, mock_model):
    mock_get_model.return_value = mock_model
    
    agent = get_agent(mock_config)
    
    assert isinstance(agent, Agent)
    mock_get_model.assert_called_once_with(config=mock_config)
    assert agent.model == mock_model
    assert agent.session_id == "engage_agent"
    assert agent.user_id == "engage_agent"
    assert agent.markdown is True
    assert agent.show_tool_calls is False
    assert agent.telemetry is False
    assert agent.monitoring is False
    assert agent.debug_mode is False
    assert isinstance(agent.storage, SqliteAgentStorage)
    assert agent.add_datetime_to_instructions is True
    assert agent.add_history_to_messages is True
    assert agent.num_history_responses == 50

@patch("engage.utils.get_model")
def test_get_agent_creates_memory_components(mock_get_model, mock_config, mock_model):
    mock_get_model.return_value = mock_model
    
    agent = get_agent(mock_config)
    
    assert isinstance(agent.memory, AgentMemory)
    assert isinstance(agent.memory.db, SqliteMemoryDb)
    assert isinstance(agent.memory.classifier, MemoryClassifier)
    assert isinstance(agent.memory.summarizer, MemorySummarizer)
    assert isinstance(agent.memory.manager, MemoryManager)
    assert agent.memory.create_user_memories is True
    assert agent.memory.create_session_summary is True
    assert agent.memory.update_user_memories_after_run is True
    assert agent.memory.update_session_summary_after_run is True

@patch("engage.utils.get_model")
def test_get_agent_empty_tools_list(mock_get_model, mock_config, mock_model):
    mock_get_model.return_value = mock_model
    
    agent = get_agent(mock_config)
    
    assert agent.tools == []

@patch("engage.utils.get_model")
def test_get_agent_description(mock_get_model, mock_config, mock_model):
    mock_get_model.return_value = mock_model
    
    agent = get_agent(mock_config)
    
    assert agent.description == "You are an expert in computer security and data analysis."

@patch("engage.utils.get_model")
def test_get_agent_empty_instructions(mock_get_model, mock_config, mock_model):
    mock_get_model.return_value = mock_model
    
    agent = get_agent(mock_config)
    
    assert agent.instructions == []
