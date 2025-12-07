import time
import schedule
from datetime import datetime
from loguru import logger
from binance_monitor.config import AppConfig
from binance_monitor.api.client import BinanceClient
from binance_monitor.notification.manager import NotificationManager
from binance_monitor.notification.models import NotificationMessage, NotificationLevel
from binance_monitor.core.strategy import StrategyAnalyzer

class MonitorEngine:
    def __init__(self, config: AppConfig, notification_manager: NotificationManager):
        self.config = config
        self.notifier = notification_manager
        self.client = BinanceClient(config.binance)
        self.strategy = StrategyAnalyzer()
        self.running = False

    def start(self):
        """启动监控引擎"""
        logger.info("Starting Monitor Engine...")
        
        # 立即运行一次
        self.run_job()
        
        # 设置定时任务
        interval = self.config.monitor.check_interval_minutes
        logger.info(f"Scheduling job every {interval} minutes")
        schedule.every(interval).minutes.do(self.run_job)
        
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def run_job(self):
        """执行一次扫描任务"""
        logger.info(f"Running scan job at {datetime.now()}")
        
        if not self.client.check_connection():
            logger.error("Cannot connect to Binance API, skipping this run.")
            return

        for symbol in self.config.monitor.symbols:
            for timeframe in self.config.monitor.timeframes:
                try:
                    self._process_pair(symbol, timeframe)
                except Exception as e:
                    logger.error(f"Error processing {symbol} {timeframe}: {e}")

    def _process_pair(self, symbol: str, timeframe: str):
        # 获取足够的数据: 1 (current) + 1 (target) + 40 (context) = 42
        # 为了保险起见，获取 50
        klines = self.client.get_klines(symbol, timeframe, limit=50)
        
        result = self.strategy.analyze(symbol, timeframe, klines)
        
        if result:
            logger.success(f"Strategy Triggered for {symbol} {timeframe}")
            message = NotificationMessage(
                title=f"Price Alert: {symbol}",
                content=result,
                level=NotificationLevel.INFO
            )
            self.notifier.send_all(message)
