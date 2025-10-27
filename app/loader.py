"""
Application loader and dependency initialization
"""
import os
import logging
from typing import Dict, Any, Optional
from tinkoff.invest import Client

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    logging.warning("python-dotenv not installed, using system environment variables")

logger = logging.getLogger(__name__)


class TinkoffInvestClient:
    """
    Client for Tinkoff Investments API
    Using https://github.com/RussianInvestments/invest-python version 0.2.0-beta117
    """
    
    def __init__(self, token: str, use_sandbox: bool = True):
        """
        Initialize Tinkoff Investments client
        
        Args:
            token: API token from Tinkoff
            use_sandbox: Use sandbox environment
        """
        self.token = token
        self.use_sandbox = use_sandbox
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        self.disconnect()
        
    def connect(self) -> bool:
        """Establish connection to Tinkoff API"""
        try:
            logger.info(f"Tinkoff client configured (sandbox: {self.use_sandbox})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Tinkoff client: {e}")
            raise
            
    def disconnect(self) -> None:
        """Close connection - в этой версии не требуется"""
        pass
            
    def get_accounts(self) -> Any:
        """Get list of accounts"""
        try:
            with Client(token=self.token) as client:
                if self.use_sandbox:
                    return client.sandbox.get_sandbox_accounts()
                else:
                    return client.users.get_accounts()
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            raise
            
    def get_portfolio(self, account_id: str) -> Any:
        """Get portfolio for account"""
        try:
            with Client(token=self.token) as client:
                if self.use_sandbox:
                    return client.sandbox.get_sandbox_portfolio(account_id=account_id)
                else:
                    return client.operations.get_portfolio(account_id=account_id)
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            raise
            
    def get_positions(self, account_id: str) -> Any:
        """Get positions for account"""
        try:
            with Client(token=self.token) as client:
                if self.use_sandbox:
                    return client.sandbox.get_sandbox_positions(account_id=account_id)
                else:
                    return client.operations.get_positions(account_id=account_id)
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
            
    def is_connected(self) -> bool:
        """Check if client is connected - всегда True в этой реализации"""
        return True

    def create_sandbox_account(self) -> Any:
        """Create sandbox account (only for sandbox mode)"""
        if not self.use_sandbox:
            raise RuntimeError("This method is only available in sandbox mode")
            
        try:
            with Client(token=self.token) as client:
                return client.sandbox.open_sandbox_account()
        except Exception as e:
            logger.error(f"Failed to create sandbox account: {e}")
            raise


def create_tinkoff_client(use_sandbox: Optional[bool] = None) -> TinkoffInvestClient:
    """
    Factory function to create Tinkoff client
    
    Args:
        use_sandbox: Use sandbox environment (default: from environment)
        
    Returns:
        TinkoffInvestClient instance
    """
    token = os.getenv('TINKOFF_TOKEN')
    if not token:
        raise ValueError("TINKOFF_TOKEN environment variable is not set. Please create .env file with TINKOFF_TOKEN")
        
    if use_sandbox is None:
        use_sandbox_str = os.getenv('TINKOFF_SANDBOX', 'true')
        use_sandbox = use_sandbox_str.lower() == 'true'
        
    return TinkoffInvestClient(token=token, use_sandbox=use_sandbox)


class DependencyLoader:
    """
    Manages application dependencies
    """
    
    def __init__(self) -> None:
        self.dependencies: Dict[str, Any] = {}
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize all application dependencies
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Starting dependency initialization...")
            
            # 1. Initialize Tinkoff client
            tinkoff_success = self._initialize_tinkoff_client()
            
            if not tinkoff_success:
                logger.warning("Tinkoff client initialization failed, using fallback...")
                self._initialize_tinkoff_fallback()
            
            # 2. Add other dependencies here as needed
            # self._initialize_other_services()
            
            self.is_initialized = True
            logger.info("All dependencies initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dependencies: {e}")
            self.cleanup()
            return False
            
    def _initialize_tinkoff_client(self) -> bool:
        """Initialize Tinkoff Investments client with robust error handling"""
        try:
            tinkoff_client = create_tinkoff_client()
            
            # Test connection with multiple fallback strategies
            if tinkoff_client.use_sandbox:
                logger.info("Testing sandbox mode connection...")
                return self._initialize_sandbox_client(tinkoff_client)
            else:
                logger.info("Testing production mode connection...")
                return self._initialize_production_client(tinkoff_client)
            
        except Exception as e:
            logger.error(f"Tinkoff client initialization failed: {e}")
            return False

    def _initialize_sandbox_client(self, tinkoff_client) -> bool:
        """Initialize sandbox client with multiple fallback strategies"""
        strategies = [
            self._try_create_sandbox_account,
            self._try_use_existing_accounts,
            self._try_basic_connection
        ]
        
        for strategy in strategies:
            try:
                if strategy(tinkoff_client):
                    self.dependencies['tinkoff_client'] = tinkoff_client
                    logger.info("✅ Tinkoff sandbox client initialized successfully")
                    return True
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        logger.error("❌ All sandbox initialization strategies failed")
        return False

    def _try_create_sandbox_account(self, tinkoff_client) -> bool:
        """Strategy 1: Try to create new sandbox account"""
        try:
            account = tinkoff_client.create_sandbox_account()
            accounts = tinkoff_client.get_accounts()
            logger.info(f"✅ New sandbox account created: {account.account_id}")
            return True
        except Exception as e:
            logger.warning(f"❌ Cannot create new sandbox account: {e}")
            return False

    def _try_use_existing_accounts(self, tinkoff_client) -> bool:
        """Strategy 2: Try to use existing sandbox accounts"""
        try:
            accounts = tinkoff_client.get_accounts()
            if accounts.accounts:
                logger.info(f"✅ Using existing sandbox account: {accounts.accounts[0].id}")
                return True
            else:
                logger.warning("❌ No existing sandbox accounts found")
                return False
        except Exception as e:
            logger.warning(f"❌ Cannot get existing accounts: {e}")
            return False

    def _try_basic_connection(self, tinkoff_client) -> bool:
        """Strategy 3: Basic connection test without account operations"""
        try:
            # Just test that we can create a client session
            with Client(token=tinkoff_client.token) as client:
                # Minimal test - just check if we can make any API call
                if tinkoff_client.use_sandbox:
                    client.sandbox.get_sandbox_accounts()
                else:
                    client.users.get_accounts()
            
            logger.info("✅ Basic connection test passed")
            return True
        except Exception as e:
            logger.warning(f"❌ Basic connection test failed: {e}")
            return False

    def _initialize_production_client(self, tinkoff_client) -> bool:
        """Initialize production client"""
        try:
            accounts = tinkoff_client.get_accounts()
            if accounts.accounts:
                logger.info(f"✅ Production accounts found: {len(accounts.accounts)}")
                self.dependencies['tinkoff_client'] = tinkoff_client
                return True
            else:
                logger.error("❌ No production accounts found")
                return False
        except Exception as e:
            logger.error(f"❌ Production initialization failed: {e}")
            return False

    def _initialize_tinkoff_fallback(self):
        """Initialize Tinkoff fallback client"""
        try:
            from app.tinkoff_fallback import create_tinkoff_fallback_client
            fallback_client = create_tinkoff_fallback_client()
            self.dependencies['tinkoff_client'] = fallback_client
            logger.info("✅ Tinkoff fallback client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Tinkoff fallback: {e}")
            raise RuntimeError("Cannot initialize Tinkoff client or fallback")
            
    def get_tinkoff_client(self):
        """Get Tinkoff client instance"""
        if not self.is_initialized:
            raise RuntimeError("Dependencies not initialized")
        
        client = self.dependencies.get('tinkoff_client')
        if client is None:
            raise RuntimeError("Tinkoff client not found in dependencies")
        return client
        
    def cleanup(self):
        """Clean up resources"""
        try:
            # Clean up Tinkoff client if it has disconnect method
            if 'tinkoff_client' in self.dependencies:
                client = self.dependencies['tinkoff_client']
                if hasattr(client, 'disconnect'):
                    client.disconnect()
                
            self.dependencies.clear()
            self.is_initialized = False
            logger.info("Dependencies cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global dependency loader instance
dependency_loader = DependencyLoader()


def initialize_app() -> bool:
    """
    Initialize the application
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Bot initialized successfully")
    return dependency_loader.initialize()


def get_tinkoff_client():
    """
    Get Tinkoff client from dependency loader
    
    Returns:
        TinkoffInvestClient instance
    """
    return dependency_loader.get_tinkoff_client()