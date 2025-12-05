import ccxt
from loguru import logger
from binance_monitor.config import BinanceConfig

class BinanceClient:
    """币安 API 客户端"""
    
    def __init__(self, config: BinanceConfig):
        # 如果只是查询行情，apiKey 和 secret 可以为空
        self.exchange = ccxt.binance({
            'apiKey': config.api_key,
            'secret': config.secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot', # 默认为现货
            }
        })
        
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

    def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            self.exchange.load_markets()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            return False
