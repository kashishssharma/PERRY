"""
Notification Management System
"""

import platform
import subprocess

class NotificationManager:
    def __init__(self):
        self.enabled = True
        self.system = platform.system()
    
    def send_notification(self, title: str, message: str):
        """Send desktop notification"""
        if not self.enabled:
            return
        
        try:
            if self.system == "Darwin":  # macOS
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', script])
            
            elif self.system == "Windows":
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Study System",
                    timeout=10
                )
            
            elif self.system == "Linux":
                subprocess.run(['notify-send', title, message])
        
        except Exception as e:
            print(f"Notification error: {e}")
    
    def toggle(self, enabled: bool):
        """Enable or disable notifications"""
        self.enabled = enabled