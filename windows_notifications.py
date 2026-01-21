# -*- coding: utf-8 -*-
# windows_notifications.py
# Windows Desktop Notifications System - FIXED VERSION

import platform
import streamlit as st
from datetime import datetime
import threading

# Platform-specific notification imports - Try multiple libraries
NOTIFICATION_METHOD = None

if platform.system() == 'Windows':
    # Try winotify first (most reliable)
    try:
        from winotify import Notification, audio
        NOTIFICATION_METHOD = 'winotify'
        print("✅ Using winotify for notifications")
    except ImportError:
        # Fallback to win10toast
        try:
            from win10toast import ToastNotifier
            NOTIFICATION_METHOD = 'win10toast'
            print("✅ Using win10toast for notifications")
        except ImportError:
            # Fallback to plyer
            try:
                from plyer import notification
                NOTIFICATION_METHOD = 'plyer'
                print("✅ Using plyer for notifications")
            except ImportError:
                NOTIFICATION_METHOD = None
                print("⚠️ No notification library available")
                print("Install with: pip install winotify")

class WindowsNotificationManager:
    """
    Manages Windows desktop notifications for schedule alerts
    """
    
    def __init__(self):
        self.system = platform.system()
        self.method = NOTIFICATION_METHOD
        self.toaster = None
        
        if self.system == 'Windows':
            if self.method == 'win10toast':
                try:
                    self.toaster = ToastNotifier()
                except Exception as e:
                    print(f"Error initializing ToastNotifier: {e}")
                    self.method = None
            
            if self.is_available():
                print(f"✅ Notifications initialized using {self.method}")
            else:
                print("⚠️ Windows notifications not available on this platform")
                print("Install winotify for best results: pip install winotify")
    
    def is_available(self):
        """Check if notifications are available"""
        return self.method is not None
    
    def send_notification(self, title, message, duration=10, icon_path=None, threaded=True):
        """
        Send a Windows desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            duration: How long to show (seconds)
            icon_path: Path to icon file (optional)
            threaded: Run in separate thread (recommended)
        
        Returns:
            bool: Success status
        """
        if not self.is_available():
            # Fallback to Streamlit toast
            st.toast(f"{title}: {message}")
            print(f"📢 Notification (in-app): {title} - {message}")
            return False
        
        try:
            if threaded:
                # Run in thread to avoid blocking
                thread = threading.Thread(
                    target=self._show_notification,
                    args=(title, message, duration, icon_path)
                )
                thread.daemon = True
                thread.start()
            else:
                self._show_notification(title, message, duration, icon_path)
            
            return True
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
            # Fallback to Streamlit toast
            st.toast(f"{title}: {message}")
            return False
    
    def _show_notification(self, title, message, duration, icon_path):
        """Internal method to show notification based on available method"""
        try:
            if self.method == 'winotify':
                self._show_winotify(title, message, duration, icon_path)
            elif self.method == 'win10toast':
                self._show_win10toast(title, message, duration, icon_path)
            elif self.method == 'plyer':
                self._show_plyer(title, message, duration, icon_path)
            
            print(f"✅ Desktop notification sent: {title}")
        except Exception as e:
            print(f"❌ Error showing notification: {e}")
    
    def _show_winotify(self, title, message, duration, icon_path):
        """Show notification using winotify (most reliable)"""
        toast = Notification(
            app_id="Mental Health & Productivity Hub",
            title=title,
            msg=message,
            duration="short" if duration <= 5 else "long"
        )
        
        # Add sound for important notifications
        if any(keyword in message.lower() for keyword in ["missed", "urgent", "blocking"]):
            toast.set_audio(audio.Reminder, loop=False)
        else:
            toast.set_audio(audio.Default, loop=False)
        
        # Set icon if provided
        if icon_path:
            try:
                toast.set_icon(icon_path)
            except:
                pass  # Icon optional
        
        # Show the notification
        toast.show()
    
    def _show_win10toast(self, title, message, duration, icon_path):
        """Show notification using win10toast"""
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon_path,
                threaded=False  # Already in thread if needed
            )
        except Exception as e:
            print(f"win10toast error: {e}")
    
    def _show_plyer(self, title, message, duration, icon_path):
        """Show notification using plyer"""
        from plyer import notification as plyer_notif
        plyer_notif.notify(
            title=title,
            message=message,
            app_name="Mental Health Hub",
            timeout=duration
        )
    
    def send_schedule_notification(self, schedule, notification_type):
        """
        Send schedule-specific notification
        
        Args:
            schedule: Schedule dictionary
            notification_type: '10min', '5min', 'start', 'missed_5', 'missed_10'
        """
        title_map = {
            '10min': '⏰ Upcoming Task',
            '5min': '⚠️ Starting Soon',
            'start': '🔔 Task Starting Now',
            'missed_5': '😟 Missed Task - 5 Minutes',
            'missed_10': '🚨 Missed Task - AUTO-BLOCKING!'
        }
        
        message_map = {
            '10min': f"{schedule['title']} starts in 10 minutes at {schedule['start_time'].strftime('%H:%M')}",
            '5min': f"{schedule['title']} starts in 5 minutes! Get ready! 💪",
            'start': f"{schedule['title']} is starting now! Time to focus! 🎯",
            'missed_5': f"You missed {schedule['title']} 5 minutes ago. Start now or sites will be blocked!",
            'missed_10': f"You missed {schedule['title']} 10 minutes ago. Distracting sites are now BLOCKED to help you focus!"
        }
        
        title = title_map.get(notification_type, '📅 Schedule Alert')
        message = message_map.get(notification_type, schedule['title'])
        
        # Longer duration for missed notifications
        duration = 20 if 'missed' in notification_type else 10
        
        return self.send_notification(title, message, duration=duration)
    
    def send_blocking_notification(self, sites_count):
        """Send notification when sites are blocked"""
        return self.send_notification(
            title='🚫 Focus Mode Activated',
            message=f'Blocked {sites_count} distracting websites to help you focus!',
            duration=12
        )
    
    def send_unblocking_notification(self):
        """Send notification when sites are unblocked"""
        return self.send_notification(
            title='✅ Focus Mode Ended',
            message='All websites have been unblocked. Great work!',
            duration=10
        )
    
    def test_notification(self):
        """Test the notification system"""
        print("🧪 Testing notification system...")
        success = self.send_notification(
            title='🧪 Test Notification',
            message='Desktop notifications are working! You will receive alerts for scheduled tasks.',
            duration=8,
            threaded=False  # Don't thread for testing
        )
        
        if success:
            print("✅ Test notification sent successfully!")
        else:
            print("⚠️ Notification sent via Streamlit toast (desktop notifications unavailable)")
        
        return success


# Singleton instance
_notification_manager = None

def get_notification_manager():
    """Get or create notification manager instance"""
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = WindowsNotificationManager()
    
    return _notification_manager


# Quick access functions
def send_desktop_notification(title, message, duration=10):
    """Quick function to send a desktop notification"""
    manager = get_notification_manager()
    return manager.send_notification(title, message, duration)


def send_schedule_alert(schedule, alert_type):
    """Quick function to send schedule-specific alert"""
    manager = get_notification_manager()
    print(f"📢 Sending schedule alert: {alert_type} for {schedule.get('title', 'Unknown')}")
    return manager.send_schedule_notification(schedule, alert_type)


def test_notifications():
    """Test the notification system - returns True if desktop notifications work"""
    manager = get_notification_manager()
    
    if not manager.is_available():
        print("\n" + "="*60)
        print("❌ DESKTOP NOTIFICATIONS NOT AVAILABLE")
        print("="*60)
        print("\nInstall a notification library:")
        print("  Recommended: pip install winotify")
        print("  Alternative: pip install win10toast")
        print("  Alternative: pip install plyer")
        print("\nAfter installation, restart the app.")
        print("="*60 + "\n")
        return False
    
    return manager.test_notification()