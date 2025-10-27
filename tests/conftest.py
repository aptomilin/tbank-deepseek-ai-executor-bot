"""
Pytest configuration for integration tests
"""
import pytest
import os
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def load_test_environment():
    """Automatically load test environment for all tests"""
    load_dotenv()
    

@pytest.fixture
def mock_tinkoff_client():
    """Fixture to mock Tinkoff API client"""
    with patch('app.loader.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def clean_dependency_loader():
    """Fixture to ensure clean dependency loader state"""
    from app.loader import dependency_loader
    original_state = dependency_loader.is_initialized
    original_dependencies = dependency_loader.dependencies.copy()
    
    yield
    
    # Restore original state
    dependency_loader.is_initialized = original_state
    dependency_loader.dependencies = original_dependencies

    """
Pytest configuration for integration tests
"""
import pytest
import os
import asyncio
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def load_test_environment():
    """Automatically load test environment for all tests"""
    load_dotenv()
    

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_telegram_update():
    """Fixture for mock Telegram update"""
    from unittest.mock import Mock
    from telegram import Update, Message, Chat, User
    
    mock_chat = Mock(spec=Chat)
    mock_chat.id = 123456789
    mock_chat.type = "private"
    
    mock_user = Mock(spec=User)
    mock_user.id = 987654321
    mock_user.first_name = "Test"
    mock_user.username = "test_user"
    
    mock_message = Mock(spec=Message)
    mock_message.message_id = 111111
    mock_message.chat = mock_chat
    mock_message.from_user = mock_user
    
    mock_update = Mock(spec=Update)
    mock_update.message = mock_message
    mock_update.effective_chat = mock_chat
    mock_update.effective_user = mock_user
    
    return mock_update


@pytest.fixture
def mock_telegram_context():
    """Fixture for mock Telegram context"""
    from unittest.mock import Mock, AsyncMock
    from telegram.ext import ContextTypes
    
    mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    mock_context.bot = Mock()
    mock_context.bot.send_message = AsyncMock()
    mock_context.bot.send_chat_action = AsyncMock()
    
    return mock_context