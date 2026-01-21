# -*- coding: utf-8 -*-
# notification_service.py
# Background Service for Desktop Notifications - FIXED TO RESPECT COMPLETIONS

"""
This script runs independently from Streamlit and sends notifications
even when you're using other applications.

HOW TO USE:
1. Save this file as "notification_service.py" in your app folder
2. Run it in a separate terminal: python notification_service.py
3. Keep it running in the background
4. Minimize the terminal - it will keep working
5. Notifications will pop up even when using other apps!
"""

import time as time_module
import pickle
import os
from datetime import datetime, timedelta
from pathlib import Path

# Import notification system
try:
    from windows_notifications import get_notification_manager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    print("⚠️ Installing winotify...")
    import subprocess
    subprocess.run(["pip", "install", "winotify"])
    from windows_notifications import get_notification_manager
    NOTIFICATIONS_AVAILABLE = True

# File to store schedules (shared with Streamlit)
SCHEDULES_FILE = "schedules_data.pkl"
NOTIFICATIONS_SENT_FILE = "notifications_sent.pkl"

class BackgroundNotificationService:
    """Background service that monitors schedules and sends notifications"""
    
    def __init__(self):
        self.notification_manager = get_notification_manager()
        self.notifications_sent = self.load_notifications_sent()
        print("\n" + "="*60)
        print("🔔 BACKGROUND NOTIFICATION SERVICE STARTED")
        print("="*60)
        print("✅ This service will send notifications even when:")
        print("   • You're using other applications")
        print("   • The Streamlit app is closed")
        print("   • Your browser is on a different tab")
        print("\n📌 Minimize this window - it will keep running!")
        print("="*60 + "\n")
    
    def load_schedules(self):
        """Load schedules from shared file - RELOADS EVERY TIME"""
        if os.path.exists(SCHEDULES_FILE):
            try:
                with open(SCHEDULES_FILE, 'rb') as f:
                    schedules = pickle.load(f)
                    # ⭐ Print status for debugging
                    completed = sum(1 for s in schedules if s.get('completed', False))
                    started = sum(1 for s in schedules if s.get('started', False))
                    print(f"📂 Loaded {len(schedules)} schedules ({completed} completed, {started} started)")
                    return schedules
            except Exception as e:
                print(f"Error loading schedules: {e}")
                return []
        return []
    
    def load_notifications_sent(self):
        """Load record of already sent notifications"""
        if os.path.exists(NOTIFICATIONS_SENT_FILE):
            try:
                with open(NOTIFICATIONS_SENT_FILE, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def save_notifications_sent(self):
        """Save record of sent notifications"""
        try:
            with open(NOTIFICATIONS_SENT_FILE, 'wb') as f:
                pickle.dump(self.notifications_sent, f)
        except Exception as e:
            print(f"Error saving notification record: {e}")
    
    def check_and_notify(self):
        """Check schedules and send notifications - FIXED VERSION"""
        # ⭐ RELOAD schedules every time to get latest status
        schedules = self.load_schedules()
        
        if not schedules:
            return
        
        now = datetime.now()
        today = now.date()
        
        for schedule in schedules:
            # ⭐ FIX 1: Skip completed schedules
            if schedule.get('completed', False):
                continue
            
            # ⭐ FIX 2: Skip started schedules
            if schedule.get('started', False):
                continue
            
            # Only check today's schedules
            if schedule['date'] != today:
                continue
            
            schedule_id = schedule['id']
            schedule_datetime = datetime.combine(schedule['date'], schedule['start_time'])
            time_diff = (schedule_datetime - now).total_seconds() / 60  # minutes
            
            # 10 minutes before
            if 9 <= time_diff <= 11:
                notif_key = f"{schedule_id}_10min"
                if notif_key not in self.notifications_sent:
                    print(f"⏰ Sending 10-minute warning for: {schedule['title']}")
                    self.notification_manager.send_schedule_notification(schedule, '10min')
                    self.notifications_sent[notif_key] = datetime.now()
                    self.save_notifications_sent()
            
            # 5 minutes before
            elif 4 <= time_diff <= 6:
                notif_key = f"{schedule_id}_5min"
                if notif_key not in self.notifications_sent:
                    print(f"⚠️ Sending 5-minute warning for: {schedule['title']}")
                    self.notification_manager.send_schedule_notification(schedule, '5min')
                    self.notifications_sent[notif_key] = datetime.now()
                    self.save_notifications_sent()
            
            # Start time
            elif -1 <= time_diff <= 1:
                notif_key = f"{schedule_id}_start"
                if notif_key not in self.notifications_sent:
                    print(f"🔔 Sending start notification for: {schedule['title']}")
                    self.notification_manager.send_schedule_notification(schedule, 'start')
                    self.notifications_sent[notif_key] = datetime.now()
                    self.save_notifications_sent()
            
            # 5 minutes after (missed)
            elif -6 <= time_diff < -4:
                notif_key = f"{schedule_id}_missed_5"
                if notif_key not in self.notifications_sent:
                    print(f"😟 Sending missed-5min warning for: {schedule['title']}")
                    self.notification_manager.send_schedule_notification(schedule, 'missed_5')
                    self.notifications_sent[notif_key] = datetime.now()
                    self.save_notifications_sent()
            
            # 10 minutes after (missed - critical)
            elif time_diff < -10:
                notif_key = f"{schedule_id}_missed_10"
                if notif_key not in self.notifications_sent:
                    print(f"🚨 Sending missed-10min critical alert for: {schedule['title']}")
                    self.notification_manager.send_schedule_notification(schedule, 'missed_10')
                    self.notifications_sent[notif_key] = datetime.now()
                    self.save_notifications_sent()
    
    def cleanup_old_notifications(self):
        """Remove notification records older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        keys_to_remove = []
        
        for key, timestamp in self.notifications_sent.items():
            if timestamp < cutoff:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.notifications_sent[key]
        
        if keys_to_remove:
            self.save_notifications_sent()
            print(f"🧹 Cleaned up {len(keys_to_remove)} old notification records")
    
    def run(self):
        """Main loop - runs forever"""
        check_count = 0
        
        while True:
            try:
                check_count += 1
                
                # ⭐ Check schedules (reloads file every time)
                self.check_and_notify()
                
                # Cleanup old records every 100 checks (~8 minutes)
                if check_count % 100 == 0:
                    self.cleanup_old_notifications()
                
                # Show heartbeat every 60 checks (~5 minutes)
                if check_count % 60 == 0:
                    schedules = self.load_schedules()
                    today_schedules = [s for s in schedules 
                                     if s['date'] == datetime.now().date() 
                                     and not s.get('completed', False)
                                     and not s.get('started', False)]
                    print(f"💓 Service running... Monitoring {len(today_schedules)} active schedules for today")
                
                # Wait 5 seconds before next check
                time_module.sleep(5)
                
            except KeyboardInterrupt:
                print("\n👋 Notification service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time_module.sleep(5)  # Continue even if error occurs


if __name__ == "__main__":
    print("\n🚀 Starting Background Notification Service...")
    print("📌 Make sure your Streamlit app is saving schedules to 'schedules_data.pkl'")
    print("\n💡 TIP: Minimize this window - notifications will still work!\n")
    
    service = BackgroundNotificationService()
    service.run()