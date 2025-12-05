import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path so we can import the package without installing it
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from binance_monitor.notification import (
    NotificationManager, 
    EmailNotifier, 
    EmailConfig, 
    NotificationMessage,
    NotificationLevel
)

class TestNotification(unittest.TestCase):
    def test_email_notifier(self):
        # Mock SMTP
        with patch("smtplib.SMTP") as mock_smtp:
            # Setup
            config = EmailConfig(
                smtp_server="smtp.test.com",
                username="user",
                password="password",
                sender_email="sender@test.com",
                receiver_email="receiver@test.com"
            )
            notifier = EmailNotifier(config)
            
            # Create message
            msg = NotificationMessage(
                title="Test Alert",
                content="This is a test.",
                level=NotificationLevel.INFO
            )
            
            # Send
            result = notifier.send(msg)
            
            # Verify
            self.assertTrue(result)
            mock_smtp.assert_called_with("smtp.test.com", 587)
            instance = mock_smtp.return_value.__enter__.return_value
            instance.login.assert_called_with("user", "password")
            instance.send_message.assert_called()

    def test_manager(self):
        manager = NotificationManager()
        mock_notifier = MagicMock()
        mock_notifier.name = "MockNotifier"
        mock_notifier.send.return_value = True
        
        manager.add_notifier(mock_notifier)
        
        msg = NotificationMessage(title="Test", content="Content")
        manager.send_all(msg)
        
        mock_notifier.send.assert_called_with(msg)

if __name__ == "__main__":
    unittest.main()
