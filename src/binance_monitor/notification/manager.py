from typing import List
from loguru import logger
from binance_monitor.notification.base import BaseNotifier
from binance_monitor.notification.models import NotificationMessage

class NotificationManager:
    """通知管理器，负责管理多个通知渠道"""
    
    def __init__(self):
        self._notifiers: List[BaseNotifier] = []

    def add_notifier(self, notifier: BaseNotifier):
        """添加通知器"""
        self._notifiers.append(notifier)
        logger.info(f"Notifier added: {notifier.name}")

    def send_all(self, message: NotificationMessage):
        """通过所有已注册的通知器发送消息"""
        if not self._notifiers:
            logger.warning("No notifiers registered, skipping notification.")
            return

        logger.info(f"Sending notification: {message.title}")
        for notifier in self._notifiers:
            try:
                success = notifier.send(message)
                if not success:
                    logger.warning(f"Failed to send via {notifier.name}")
            except Exception as e:
                logger.error(f"Error in {notifier.name}: {e}")
