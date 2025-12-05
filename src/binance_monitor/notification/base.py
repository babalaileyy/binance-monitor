from abc import ABC, abstractmethod
from binance_monitor.notification.models import NotificationMessage

class BaseNotifier(ABC):
    """通知器抽象基类，所有具体的通知方式（邮件、微信等）都应继承此类"""
    
    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """
        发送通知
        :param message: 通知消息对象
        :return: 发送是否成功
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """通知器名称"""
        pass
