import unittest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from binance_monitor.core.strategy import StrategyAnalyzer

class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.analyzer = StrategyAnalyzer()

    def create_mock_kline(self, open_p, high_p, low_p, close_p, timestamp=None):
        return {
            'open': float(open_p),
            'high': float(high_p),
            'low': float(low_p),
            'close': float(close_p),
            'timestamp': timestamp or int(datetime.now().timestamp() * 1000)
        }

    def test_is_pinbar_bullish(self):
        """测试看涨 Pinbar (Hammer)"""
        # Lower shadow long, body small near top
        # High=100, Low=80, Open=98, Close=99
        # Total=20. Lower shadow = 98-80 = 18. Ratio = 18/20 = 0.9 > 0.66
        kline = self.create_mock_kline(98, 100, 80, 99)
        self.assertTrue(self.analyzer._is_pinbar(kline))
        self.assertEqual(self.analyzer._get_main_shadow_direction(kline), "DOWN")

    def test_is_pinbar_bearish(self):
        """测试看跌 Pinbar (Shooting Star)"""
        # Upper shadow long, body small near bottom
        # High=100, Low=80, Open=81, Close=82
        # Total=20. Upper shadow = 100-82 = 18. Ratio = 0.9
        kline = self.create_mock_kline(81, 100, 80, 82)
        self.assertTrue(self.analyzer._is_pinbar(kline))
        self.assertEqual(self.analyzer._get_main_shadow_direction(kline), "UP")

    def test_not_pinbar(self):
        # Normal candle
        kline = self.create_mock_kline(90, 100, 80, 95)
        self.assertFalse(self.analyzer._is_pinbar(kline))

    def test_context_bearish_valid(self):
        """测试看跌Pinbar + 有效上下文"""
        # Pinbar: High=110, Low=90, Open=91, Close=92 (UP shadow dominant)
        # Prev 40 Highs max = 115
        # |110 - 115| = 5. Pinbar Len = 20. 5 < 20. Valid.
        pinbar = self.create_mock_kline(91, 110, 90, 92)
        
        prev_klines = []
        for i in range(40):
            prev_klines.append(self.create_mock_kline(100, 115, 95, 105)) # Highs around 115
            
        self.assertTrue(self.analyzer._check_context(pinbar, prev_klines))

    def test_context_bearish_invalid(self):
        """测试看跌Pinbar + 无效上下文"""
        # Pinbar: High=110, Low=90 (Len=20)
        # Prev Max High = 150
        # |110 - 150| = 40. > 20. Invalid.
        pinbar = self.create_mock_kline(91, 110, 90, 92)
        
        prev_klines = []
        for i in range(40):
            prev_klines.append(self.create_mock_kline(140, 150, 130, 145))
            
        self.assertFalse(self.analyzer._check_context(pinbar, prev_klines))

if __name__ == '__main__':
    unittest.main()
