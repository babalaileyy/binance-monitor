import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from binance_monitor.api import BinanceClient
from binance_monitor.config import BinanceConfig

class TestBinanceAPI(unittest.TestCase):
    def test_get_price(self):
        # Mock ccxt
        with patch("ccxt.binance") as mock_binance:
            # Setup
            mock_exchange = MagicMock()
            mock_binance.return_value = mock_exchange
            mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
            
            config = BinanceConfig()
            client = BinanceClient(config)
            
            # Test
            price = client.get_price("BTC/USDT")
            
            # Verify
            self.assertEqual(price, 50000.0)
            mock_exchange.fetch_ticker.assert_called_with("BTC/USDT")

    @patch("ccxt.binance")
    def test_connection_error(self, mock_binance):
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange
        mock_exchange.load_markets.side_effect = Exception("Network Error")
        
        client = BinanceClient(BinanceConfig())
        self.assertFalse(client.check_connection())

if __name__ == "__main__":
    unittest.main()
