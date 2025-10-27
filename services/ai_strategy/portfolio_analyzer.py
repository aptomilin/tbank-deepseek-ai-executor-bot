import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """Анализатор портфеля для подготовки данных к AI анализу"""
    
    def __init__(self):
        self.risk_metrics = {}
        
    def prepare_portfolio_for_analysis(self, raw_portfolio: Dict) -> Dict[str, Any]:
        """
        Подготовка портфеля для AI анализа
        
        Args:
            raw_portfolio: Сырые данные портфеля
            
        Returns:
            Структурированные данные для анализа
        """
        try:
            positions = raw_portfolio.get('positions', [])
            
            # Расчет метрик
            total_value = raw_portfolio.get('total_value', 0)
            position_metrics = self._calculate_position_metrics(positions, total_value)
            
            prepared_data = {
                "summary": {
                    "total_value": total_value,
                    "currency": "RUB",
                    "positions_count": len(positions),
                    "analysis_date": datetime.now().isoformat()
                },
                "allocations": {
                    "by_asset_class": self._calculate_asset_allocation(positions),
                    "by_sector": self._calculate_sector_allocation(positions),
                    "by_currency": self._calculate_currency_allocation(positions)
                },
                "performance": {
                    "total_return": raw_portfolio.get('performance', {}).get('total_return', 0),
                    "daily_change": raw_portfolio.get('performance', {}).get('daily_change', 0),
                    "volatility_estimate": self._estimate_volatility(positions)
                },
                "risk_metrics": {
                    "concentration_risk": self._calculate_concentration_risk(positions),
                    "liquidity_risk": self._assess_liquidity_risk(positions),
                    "market_risk": self._assess_market_risk(positions)
                },
                "positions_detail": position_metrics
            }
            
            return prepared_data
            
        except Exception as e:
            logger.error(f"Portfolio preparation error: {e}")
            return {}
    
    def _calculate_position_metrics(self, positions: List[Dict], total_value: float) -> List[Dict]:
        """Расчет метрик для каждой позиции"""
        metrics = []
        
        for position in positions:
            current_price = position.get('current_price', 0)
            quantity = position.get('quantity', 0)
            position_value = current_price * quantity
            
            if total_value > 0:
                weight = (position_value / total_value) * 100
            else:
                weight = 0
                
            avg_price = position.get('average_price', 0)
            if avg_price > 0:
                unrealized_pl = ((current_price - avg_price) / avg_price) * 100
            else:
                unrealized_pl = 0
                
            metrics.append({
                "ticker": position.get('ticker', 'Unknown'),
                "name": position.get('name', 'Unknown'),
                "weight_percent": round(weight, 2),
                "unrealized_pl_percent": round(unrealized_pl, 2),
                "position_value": round(position_value, 2),
                "quantity": quantity,
                "current_price": current_price,
                "average_price": avg_price,
                "instrument_type": position.get('type', 'unknown'),
                "sector": position.get('sector', 'other')
            })
        
        return metrics
    
    def _calculate_asset_allocation(self, positions: List[Dict]) -> Dict[str, float]:
        """Расчет распределения по классам активов"""
        allocation = {
            "stocks": 0.0,
            "bonds": 0.0,
            "etf": 0.0,
            "cash": 0.0,
            "other": 0.0
        }
        
        for position in positions:
            instrument_type = position.get('type', 'other').lower()
            weight = position.get('weight', 0)
            
            if 'stock' in instrument_type:
                allocation['stocks'] += weight
            elif 'bond' in instrument_type:
                allocation['bonds'] += weight
            elif 'etf' in instrument_type:
                allocation['etf'] += weight
            elif 'currency' in instrument_type:
                allocation['cash'] += weight
            else:
                allocation['other'] += weight
        
        return {k: round(v, 2) for k, v in allocation.items()}
    
    def _calculate_sector_allocation(self, positions: List[Dict]) -> Dict[str, float]:
        """Расчет распределения по секторам"""
        sectors = {}
        
        for position in positions:
            sector = position.get('sector', 'other')
            weight = position.get('weight', 0)
            
            if sector in sectors:
                sectors[sector] += weight
            else:
                sectors[sector] = weight
        
        return {k: round(v, 2) for k, v in sectors.items()}
    
    def _calculate_currency_allocation(self, positions: List[Dict]) -> Dict[str, float]:
        """Расчет распределения по валютам"""
        return {"RUB": 100.0}
    
    def _estimate_volatility(self, positions: List[Dict]) -> float:
        """Оценка волатильности портфеля"""
        volatility_score = 0.0
        total_weight = 0.0
        
        for position in positions:
            weight = position.get('weight', 0) / 100.0
            instrument_type = position.get('type', '').lower()
            
            if 'stock' in instrument_type:
                volatility_score += weight * 0.8
            elif 'bond' in instrument_type:
                volatility_score += weight * 0.3
            elif 'etf' in instrument_type:
                volatility_score += weight * 0.6
            else:
                volatility_score += weight * 0.5
                
            total_weight += weight
        
        if total_weight > 0:
            return round(volatility_score / total_weight * 100, 2)
        return 50.0
    
    def _calculate_concentration_risk(self, positions: List[Dict]) -> str:
        """Оценка риска концентрации"""
        if not positions:
            return "low"
            
        weights = [p.get('weight', 0) for p in positions]
        max_weight = max(weights) if weights else 0
        
        if max_weight > 30:
            return "high"
        elif max_weight > 15:
            return "medium"
        else:
            return "low"
    
    def _assess_liquidity_risk(self, positions: List[Dict]) -> str:
        """Оценка риска ликвидности"""
        liquid_instruments = ['SBER', 'GAZP', 'LKOH', 'ROSN', 'TCS']
        liquid_weight = 0.0
        
        for position in positions:
            ticker = position.get('ticker', '')
            if any(liq in ticker for liq in liquid_instruments):
                liquid_weight += position.get('weight', 0)
        
        if liquid_weight >= 70:
            return "low"
        elif liquid_weight >= 40:
            return "medium"
        else:
            return "high"
    
    def _assess_market_risk(self, positions: List[Dict]) -> str:
        """Оценка рыночного риска"""
        stock_weight = 0.0
        
        for position in positions:
            if 'stock' in position.get('type', '').lower():
                stock_weight += position.get('weight', 0)
        
        if stock_weight >= 80:
            return "high"
        elif stock_weight >= 50:
            return "medium"
        else:
            return "low"