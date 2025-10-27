"""
Fallback Tinkoff client when API is unavailable
"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class TinkoffFallbackClient:
    """Fallback Tinkoff client with mock data"""
    
    def __init__(self):
        self.use_sandbox = True
        self.token = "fallback_token"
        logger.info("✅ Tinkoff Fallback Client initialized")
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    def connect(self):
        """Mock connect method"""
        return True
            
    def disconnect(self):
        """Mock disconnect method"""
        pass
    
    def get_accounts(self):
        """Return mock accounts"""
        class MockAccountsResponse:
            def __init__(self):
                self.accounts = [MockAccount()]
        
        class MockAccount:
            def __init__(self):
                self.id = "fallback_account_001"
                self.name = "Fallback Investment Account"
                self.status = "ACTIVE"
                self.type = "Tinkoff"
        
        return MockAccountsResponse()
    
    def get_portfolio(self, account_id: str):
        """Return mock portfolio"""
        class MockPortfolioResponse:
            def __init__(self):
                self.total_amount_shares = MockMoneyValue(units=100000, nano=0)
                self.total_amount_bonds = MockMoneyValue(units=50000, nano=0)
                self.total_amount_etf = MockMoneyValue(units=25000, nano=0)
                self.total_amount_currencies = MockMoneyValue(units=10000, nano=0)
                self.expected_yield = MockQuotation(units=15000, nano=0)
                self.positions = [
                    MockPosition(figi="SBER0000000000", instrument_type="share", quantity=MockQuotation(units=100, nano=0), average_position_price=MockMoneyValue(units=250, nano=0)),
                    MockPosition(figi="GAZP0000000000", instrument_type="share", quantity=MockQuotation(units=50, nano=0), average_position_price=MockMoneyValue(units=160, nano=0)),
                    MockPosition(figi="VTBR0000000000", instrument_type="share", quantity=MockQuotation(units=200, nano=0), average_position_price=MockMoneyValue(units=0.025, nano=0)),
                    MockPosition(figi="SU26238RMFS4", instrument_type="bond", quantity=MockQuotation(units=10, nano=0), average_position_price=MockMoneyValue(units=1000, nano=0)),
                ]
        
        class MockMoneyValue:
            def __init__(self, units: int, nano: int):
                self.units = units
                self.nano = nano
                self.currency = "rub"
        
        class MockQuotation:
            def __init__(self, units: int, nano: int):
                self.units = units
                self.nano = nano
        
        class MockPosition:
            def __init__(self, figi: str, instrument_type: str, quantity: MockQuotation, average_position_price: MockMoneyValue):
                self.figi = figi
                self.instrument_type = instrument_type
                self.quantity = quantity
                self.average_position_price = average_position_price
                self.expected_yield = MockQuotation(units=500, nano=0)
                self.current_nkd = MockQuotation(units=0, nano=0)
                self.current_price = MockMoneyValue(units=average_position_price.units + 10, nano=0)
        
        return MockPortfolioResponse()
    
    def get_positions(self, account_id: str):
        """Return mock positions"""
        class MockPositionsResponse:
            def __init__(self):
                self.money = [
                    MockMoneyValue(currency="RUB", units=10000, nano=0),
                    MockMoneyValue(currency="USD", units=500, nano=0)
                ]
                self.securities = [
                    MockPositionsSecurity(figi="SBER0000000000", instrument_type="share", balance=100, blocked=0),
                    MockPositionsSecurity(figi="GAZP0000000000", instrument_type="share", balance=50, blocked=0),
                    MockPositionsSecurity(figi="VTBR0000000000", instrument_type="share", balance=200, blocked=0),
                    MockPositionsSecurity(figi="SU26238RMFS4", instrument_type="bond", balance=10, blocked=0),
                ]
                self.futures = []
                self.options = []
        
        class MockMoneyValue:
            def __init__(self, currency: str, units: int, nano: int):
                self.currency = currency
                self.units = units
                self.nano = nano
        
        class MockPositionsSecurity:
            def __init__(self, figi: str, instrument_type: str, balance: int, blocked: int):
                self.figi = figi
                self.instrument_type = instrument_type
                self.balance = balance
                self.blocked = blocked
        
        return MockPositionsResponse()
    
    def create_sandbox_account(self):
        """Mock sandbox account creation"""
        class MockSandboxAccount:
            def __init__(self):
                self.account_id = "fallback_sandbox_account_001"
        
        return MockSandboxAccount()
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return True


def create_tinkoff_fallback_client():
    """Create fallback Tinkoff client"""
    return TinkoffFallbackClient()