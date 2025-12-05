import sys
import os
from datetime import datetime
from loguru import logger

# 添加 src 到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from binance_monitor.api import BinanceClient
from binance_monitor.config import BinanceConfig

def format_timestamp(ts):
    """将毫秒时间戳转换为可读时间"""
    return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')

def test_klines():
    """测试 K 线数据获取"""
    try:
        config = BinanceConfig()
        client = BinanceClient(config)
        
        symbol = "BTC/USDT"
        timeframe = "4h"
        
        logger.info(f"Fetching {timeframe} klines for {symbol}...")
        
        # 获取最近的 K 线数据
        klines = client.get_klines(symbol, timeframe=timeframe, limit=5)
        
        if not klines:
            logger.error("No kline data received")
            return

        # 打印数据
        logger.info(f"Received {len(klines)} candles:")
        
        for i, kline in enumerate(klines):
            ts = format_timestamp(kline['timestamp'])
            logger.info(f"Candle {i} [{ts}] | Open: {kline['open']} | High: {kline['high']} | Low: {kline['low']} | Close: {kline['close']}")

        # 分析：比较上一根 K 线（已收盘）和当前 K 线（可能未收盘）
        if len(klines) >= 2:
            current_candle = klines[0]
            prev_candle = klines[1]
            
            logger.info("-" * 50)
            logger.info("Analysis:")
            logger.info(f"Previous Candle ({format_timestamp(prev_candle['timestamp'])}):")
            logger.info(f"  High: {prev_candle['high']}")
            logger.info(f"  Low:  {prev_candle['low']}")
            logger.info(f"  Close: {prev_candle['close']}")
            
            logger.info(f"Current Candle ({format_timestamp(current_candle['timestamp'])}):")
            logger.info(f"  Current Price: {current_candle['close']}")
            
            # 简单的形态判断示例
            if current_candle['close'] > prev_candle['high']:
                logger.success("BULLISH SIGNAL: Current price broke above previous high!")
            elif current_candle['close'] < prev_candle['low']:
                logger.warning("BEARISH SIGNAL: Current price broke below previous low!")
            else:
                logger.info("Price is within previous candle's range.")

    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_klines()
