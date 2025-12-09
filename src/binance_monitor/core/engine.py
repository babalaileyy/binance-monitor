import time
import schedule
from datetime import datetime
from croniter import croniter
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
        
        self.running = True
        
        # 获取 Cron 表达式，如果没有配置则默认每小时
        cron_expr = self.config.monitor.cron_expression
        if not cron_expr:
            logger.warning("No cron_expression found, using default interval loop (not recommended).")
            # 这里可以保留旧逻辑或强制要求配置
            # 为了简单起见，如果没有 cron，我们构造一个基于 interval 的简单 cron 或者报错
            # 这里我们假设用户配置了 cron
            return

        logger.info(f"Using Cron expression: {cron_expr}")

        while self.running:
            now = datetime.now()
            
            try:
                # 使用 croniter 计算下一次运行时间
                iter = croniter(cron_expr, now)
                next_run_time = iter.get_next(datetime)
                
                wait_seconds = (next_run_time - now).total_seconds()
                
                logger.info(f"Next scan scheduled at {next_run_time} (waiting {wait_seconds:.2f} seconds)")
                
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
                
                self.run_job()
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # 防止死循环报错，休眠一会
                time.sleep(60)

    def run_job(self):
        """执行一次扫描任务"""
        logger.info(f"Running scan job at {datetime.now()}")
        
        if not self.client.check_connection():
            logger.error("Cannot connect to Binance API, skipping this run.")
            return

        # 收集所有的分析结果
        results = []

        for symbol in self.config.monitor.symbols:
            for timeframe in self.config.monitor.timeframes:
                try:
                    res = self._process_pair(symbol, timeframe)
                    if res and res.get("is_pinbar"):
                        results.append(res)
                except Exception as e:
                    logger.error(f"Error processing {symbol} {timeframe}: {e}")

        # 如果有结果，汇总发送邮件
        if results:
            self._send_consolidated_report(results)
        else:
            logger.info("No Pinbars detected in this scan.")

    def _process_pair(self, symbol: str, timeframe: str):
        # 获取足够的数据: 1 (current) + 1 (target) + 40 (context) = 42
        # 为了保险起见，获取 50
        klines = self.client.get_klines(symbol, timeframe, limit=50)
        return self.strategy.analyze(symbol, timeframe, klines)

    def _send_consolidated_report(self, results):
        """发送汇总报告"""
        # 按优先级排序，重点在前
        results.sort(key=lambda x: x["is_priority"], reverse=True)
        
        title = f"监控报告 - 发现 {len(results)} 个 Pinbar 形态"
        
        content_lines = []
        content_lines.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_lines.append("=" * 30)
        content_lines.append("")
        
        for res in results:
            symbol = res["symbol"]
            timeframe = res["timeframe"]
            priority_mark = "【重点】" if res["is_priority"] else ""
            
            # 格式化时间戳
            ts = res['timestamp']
            try:
                dt_obj = datetime.fromtimestamp(ts / 1000)
                time_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = str(ts)

            line = f"{priority_mark} 交易对: {symbol} ({timeframe})"
            content_lines.append(line)
            content_lines.append(f"K线时间: {time_str}")
            content_lines.append(f"详情: {res['details']}")
            content_lines.append("")
            content_lines.append("-" * 30)
            content_lines.append("")
            
        # 将换行符转换为 HTML 的 <br>
        full_content = "<br>".join(content_lines)
        
        message = NotificationMessage(
            title=title,
            content=full_content,
            level=NotificationLevel.INFO
        )
        self.notifier.send_all(message)
        logger.success("Consolidated report sent.")
