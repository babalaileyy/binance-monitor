from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class NotificationLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

class NotificationMessage(BaseModel):
    """通知消息模型"""
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    level: NotificationLevel = Field(default=NotificationLevel.INFO, description="通知级别")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成时间")
