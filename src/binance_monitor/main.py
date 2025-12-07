import sys
import os
from loguru import logger
from binance_monitor.config import load_config
from binance_monitor.notification import EmailNotifier, NotificationManager
from binance_monitor.core.engine import MonitorEngine

def main():
    try:
        # 1. Load Config
        config = load_config()
        logger.info("Configuration loaded.")

        # 2. Setup Notification
        notification_manager = NotificationManager()
        email_notifier = EmailNotifier(config.email)
        notification_manager.add_notifier(email_notifier)
        
        # 3. Setup and Start Engine
        engine = MonitorEngine(config, notification_manager)
        engine.start()

    except KeyboardInterrupt:
        logger.info("Monitor stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
