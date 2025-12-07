import ccxt
from typing import List, Dict, Any, Optional
from loguru import logger
from binance_monitor.config import BinanceConfig

class BinanceClient:
    """币安 API 客户端"""
    
    def __init__(self, config: BinanceConfig):
        # 如果只是查询行情，apiKey 和 secret 可以为空
        options = {
            'apiKey': config.api_key,
            'secret': config.secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot', # 默认为现货
            }
        }
        
        # 配置代理
        if config.http_proxy or config.https_proxy:
            proxies = {}
            if config.http_proxy:
                proxies['http'] = config.http_proxy
            if config.https_proxy:
                proxies['https'] = config.https_proxy
            options['proxies'] = proxies
            
        self.exchange = ccxt.binance(options)
        
    def get_price(self, symbol: str) -> float:
        """
        获取当前交易对价格
        :param symbol: 交易对，如 'BTC/USDT'
        :return: 当前价格
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker.get('last')
            if price is None:
                raise ValueError(f"Could not fetch price for {symbol}")
            return float(price)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise

    def get_klines(self, symbol: str, timeframe: str = '4h', limit: int = 2) -> List[Dict[str, Any]]:
        """
        获取 K 线数据
        :param symbol: 交易对，如 'BTC/USDT'
        :param timeframe: 时间周期，如 '1m', '1h', '4h', '1d'
        :param limit: 获取数量，默认 2 (用于比较上一根和当前这根)
        :return: K 线数据列表，每项包含 timestamp, open, high, low, close, volume
        """
        try:
            # fetch_ohlcv 返回格式: [timestamp, open, high, low, close, volume]
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            results = []
            for candle in ohlcv:
                results.append({
                    'timestamp': candle[0],
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                })
            
            # 按时间倒序排列（最新的在前面）
            return sorted(results, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol} ({timeframe}): {e}")
            raise

    def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            self.exchange.load_markets()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            return False
