import sys
import os
from loguru import logger

# 添加 src 到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from binance_monitor.api import BinanceClient
from binance_monitor.config import BinanceConfig

def test_real_api():
    """测试真实的币安 API 连接和价格查询"""
    try:
        # 使用空配置（匿名模式）
        config = BinanceConfig()
        client = BinanceClient(config)
        
        logger.info("Connecting to Binance...")
        if client.check_connection():
            logger.success("Connected to Binance successfully!")
        else:
            logger.error("Failed to connect to Binance.")
            return

        # 测试获取价格
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        for symbol in symbols:
            logger.info(f"Fetching price for {symbol}...")
            price = client.get_price(symbol)
            logger.success(f"Current {symbol} price: {price}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_real_api()
