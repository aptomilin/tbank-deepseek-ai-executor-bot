"""
Regression tests for TinkoffInvestClient
"""
import os
import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from app.loader import TinkoffInvestClient, create_tinkoff_client

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestTinkoffInvestClient:
    """Test cases for TinkoffInvestClient"""
    
    def setup_method(self):
        """Setup for each test"""
        self.test_token = "test_token_123"
        self.account_id = "test_account_123"
        
    def test_client_initialization(self):
        """Test client initialization with different parameters"""
        # Test with sandbox enabled
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        assert client.token == self.test_token
        assert client.use_sandbox is True
        
        # Test with sandbox disabled
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        assert client.token == self.test_token
        assert client.use_sandbox is False
        
    def test_context_manager(self):
        """Test client as context manager"""
        with TinkoffInvestClient(token=self.test_token, use_sandbox=True) as client:
            assert client.token == self.test_token
            assert client.use_sandbox is True
            assert client.is_connected() is True
            
    @patch('app.loader.Client')
    def test_get_accounts_sandbox(self, mock_client_class):
        """Test getting accounts in sandbox mode"""
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_sandbox_accounts = MagicMock()
        mock_sandbox_accounts.accounts = [MagicMock(), MagicMock()]
        mock_client_instance.sandbox.get_sandbox_accounts.return_value = mock_sandbox_accounts
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        accounts = client.get_accounts()
        
        # Verify the correct methods were called
        mock_client_class.assert_called_with(token=self.test_token)
        mock_client_instance.sandbox.get_sandbox_accounts.assert_called_once()
        assert len(accounts.accounts) == 2
        
    @patch('app.loader.Client')
    def test_get_accounts_production(self, mock_client_class):
        """Test getting accounts in production mode"""
        # Mock the client and its methods
        mock_client_instance = MagicMock()
        mock_accounts = MagicMock()
        mock_accounts.accounts = [MagicMock()]
        mock_client_instance.users.get_accounts.return_value = mock_accounts
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        accounts = client.get_accounts()
        
        # Verify the correct methods were called
        mock_client_class.assert_called_with(token=self.test_token)
        mock_client_instance.users.get_accounts.assert_called_once()
        assert len(accounts.accounts) == 1
        
    @patch('app.loader.Client')
    def test_get_portfolio_sandbox(self, mock_client_class):
        """Test getting portfolio in sandbox mode"""
        mock_client_instance = MagicMock()
        mock_portfolio = MagicMock()
        mock_client_instance.sandbox.get_sandbox_portfolio.return_value = mock_portfolio
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        portfolio = client.get_portfolio(self.account_id)
        
        mock_client_instance.sandbox.get_sandbox_portfolio.assert_called_once_with(
            account_id=self.account_id
        )
        assert portfolio == mock_portfolio
        
    @patch('app.loader.Client')
    def test_get_portfolio_production(self, mock_client_class):
        """Test getting portfolio in production mode"""
        mock_client_instance = MagicMock()
        mock_portfolio = MagicMock()
        mock_client_instance.operations.get_portfolio.return_value = mock_portfolio
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        portfolio = client.get_portfolio(self.account_id)
        
        mock_client_instance.operations.get_portfolio.assert_called_once_with(
            account_id=self.account_id
        )
        assert portfolio == mock_portfolio
        
    @patch('app.loader.Client')
    def test_get_positions_sandbox(self, mock_client_class):
        """Test getting positions in sandbox mode"""
        mock_client_instance = MagicMock()
        mock_positions = MagicMock()
        mock_client_instance.sandbox.get_sandbox_positions.return_value = mock_positions
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        positions = client.get_positions(self.account_id)
        
        mock_client_instance.sandbox.get_sandbox_positions.assert_called_once_with(
            account_id=self.account_id
        )
        assert positions == mock_positions
        
    @patch('app.loader.Client')
    def test_get_positions_production(self, mock_client_class):
        """Test getting positions in production mode"""
        mock_client_instance = MagicMock()
        mock_positions = MagicMock()
        mock_client_instance.operations.get_positions.return_value = mock_positions
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        positions = client.get_positions(self.account_id)
        
        mock_client_instance.operations.get_positions.assert_called_once_with(
            account_id=self.account_id
        )
        assert positions == mock_positions
        
    @patch('app.loader.Client')
    def test_create_sandbox_account(self, mock_client_class):
        """Test creating sandbox account"""
        mock_client_instance = MagicMock()
        mock_account_response = MagicMock()
        mock_client_instance.sandbox.open_sandbox_account.return_value = mock_account_response
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        account_response = client.create_sandbox_account()
        
        mock_client_instance.sandbox.open_sandbox_account.assert_called_once()
        assert account_response == mock_account_response
        
    def test_create_sandbox_account_production_mode(self):
        """Test that creating sandbox account fails in production mode"""
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        
        with pytest.raises(RuntimeError, match="This method is only available in sandbox mode"):
            client.create_sandbox_account()
            
    def test_is_connected(self):
        """Test is_connected method always returns True"""
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        assert client.is_connected() is True
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        assert client.is_connected() is True


class TestTinkoffClientFactory:
    """Test cases for create_tinkoff_client factory function"""
    
    def setup_method(self):
        """Setup for each test"""
        self.original_env = os.environ.copy()
        
    def teardown_method(self):
        """Restore environment after each test"""
        os.environ.clear()
        os.environ.update(self.original_env)
        
    @patch.dict(os.environ, {'TINKOFF_TOKEN': 'test_token_456', 'TINKOFF_SANDBOX': 'true'})
    def test_create_client_with_env_vars(self):
        """Test creating client with environment variables"""
        client = create_tinkoff_client()
        
        assert client.token == 'test_token_456'
        assert client.use_sandbox is True
        
    @patch.dict(os.environ, {'TINKOFF_TOKEN': 'test_token_456', 'TINKOFF_SANDBOX': 'false'})
    def test_create_client_sandbox_false(self):
        """Test creating client with sandbox disabled"""
        client = create_tinkoff_client()
        
        assert client.token == 'test_token_456'
        assert client.use_sandbox is False
        
    @patch.dict(os.environ, {'TINKOFF_TOKEN': 'test_token_456'})
    def test_create_client_default_sandbox(self):
        """Test creating client with default sandbox value"""
        client = create_tinkoff_client()
        
        assert client.token == 'test_token_456'
        assert client.use_sandbox is True  # default value
        
    def test_create_client_missing_token(self):
        """Test creating client without token raises error"""
        # Ensure TINKOFF_TOKEN is not set
        if 'TINKOFF_TOKEN' in os.environ:
            del os.environ['TINKOFF_TOKEN']
            
        with pytest.raises(ValueError, match="TINKOFF_TOKEN environment variable is not set"):
            create_tinkoff_client()
            
    @patch.dict(os.environ, {'TINKOFF_TOKEN': 'test_token_456'})
    def test_create_client_with_parameter_override(self):
        """Test creating client with parameter override"""
        client = create_tinkoff_client(use_sandbox=False)
        
        assert client.token == 'test_token_456'
        assert client.use_sandbox is False


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Setup for each test"""
        self.test_token = "test_token_123"
        
    @patch('app.loader.Client')
    def test_api_error_handling(self, mock_client_class):
        """Test that API errors are properly handled and re-raised"""
        mock_client_instance = MagicMock()
        mock_client_instance.users.get_accounts.side_effect = Exception("API Error")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        
        # The original exception should be re-raised
        with pytest.raises(Exception, match="API Error"):
            client.get_accounts()
            
    @patch('app.loader.Client')
    def test_connection_error(self, mock_client_class):
        """Test connection error handling"""
        mock_client_class.side_effect = ConnectionError("Connection failed")
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=True)
        
        # The original connection error should be re-raised
        with pytest.raises(ConnectionError, match="Connection failed"):
            client.get_accounts()


class TestErrorLogging:
    """Test error logging scenarios"""
    
    def setup_method(self):
        """Setup for each test"""
        self.test_token = "test_token_123"
        
    @patch('app.loader.Client')
    def test_error_logging(self, mock_client_class, caplog):
        """Test that errors are properly logged"""
        mock_client_instance = MagicMock()
        mock_client_instance.users.get_accounts.side_effect = Exception("Test error")
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        client = TinkoffInvestClient(token=self.test_token, use_sandbox=False)
        
        with caplog.at_level(logging.ERROR):
            try:
                client.get_accounts()
            except Exception:
                pass  # We're testing logging, not the exception itself
            
            # Check that the error was logged
            assert "Failed to get accounts" in caplog.text
            assert "Test error" in caplog.text


def test_integration_flow():
    """Integration test simulating the main application flow"""
    # This test verifies the complete flow without actual API calls
    with patch('app.loader.Client') as mock_client_class:
        mock_client_instance = MagicMock()
        mock_accounts = MagicMock()
        mock_accounts.accounts = [MagicMock(id='acc1'), MagicMock(id='acc2')]
        mock_client_instance.sandbox.get_sandbox_accounts.return_value = mock_accounts
        mock_client_instance.sandbox.open_sandbox_account.return_value = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client_instance
        
        # Simulate the main application initialization flow
        client = create_tinkoff_client()
        assert client.use_sandbox is True
        
        # Test account creation and retrieval
        account_response = client.create_sandbox_account()
        accounts = client.get_accounts()
        
        assert len(accounts.accounts) == 2
        mock_client_instance.sandbox.open_sandbox_account.assert_called_once()
        mock_client_instance.sandbox.get_sandbox_accounts.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])