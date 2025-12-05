import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr, Field
from loguru import logger
from binance_monitor.notification.base import BaseNotifier
from binance_monitor.notification.models import NotificationMessage

class EmailConfig(BaseModel):
    """邮件配置模型"""
    smtp_server: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(587, description="SMTP端口")
    username: str = Field(..., description="登录用户名")
    password: str = Field(..., description="登录密码或应用授权码")
    sender_email: EmailStr = Field(..., description="发件人邮箱")
    receiver_email: EmailStr = Field(..., description="收件人邮箱")
    use_tls: bool = Field(True, description="是否使用TLS加密")

class EmailNotifier(BaseNotifier):
    """邮件通知实现"""

    def __init__(self, config: EmailConfig):
        self.config = config

    @property
    def name(self) -> str:
        return "EmailNotifier"

    def send(self, message: NotificationMessage) -> bool:
        try:
            # 构建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = self.config.receiver_email
            msg['Subject'] = f"[{message.level.value}] {message.title}"

            # 邮件正文
            body = f"""
            <h2>{message.title}</h2>
            <p><strong>级别:</strong> {message.level.value}</p>
            <p><strong>时间:</strong> {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p>{message.content}</p>
            """
            msg.attach(MIMEText(body, 'html'))

            # 连接 SMTP 服务器
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {self.config.receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
