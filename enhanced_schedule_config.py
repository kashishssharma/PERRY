# -*- coding: utf-8 -*-
# Enhanced Schedule Management with Windows Notifications - FIXED

from datetime import datetime, timedelta
import streamlit as st
from collections import defaultdict

# Import notification manager
try:
    from windows_notifications import get_notification_manager, send_schedule_alert
    NOTIFICATIONS_AVAILABLE = True
    print("✅ Notification module imported successfully")
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("⚠️ Windows notifications not available")

# Import existing dependencies
from activity_logger import ACTIVITY_TYPES, log_user_activity


def check_schedule_notifications_with_desktop_alerts():
    """
    Enhanced notification system with Windows desktop notifications
    
    Returns: list of notifications with actions
    """
    now = datetime.now()
    today = now.date()
    
    # Check every 30 seconds for responsiveness
    if 'last_notification_check' not in st.session_state:
        st.session_state.last_notification_check = now
    
    time_since_check = (now - st.session_state.last_notification_check).seconds
    if time_since_check < 30:
        return []
    
    st.session_state.last_notification_check = now
    new_notifications = []
    
    # Get notification manager
    notif_manager = get_notification_manager() if NOTIFICATIONS_AVAILABLE else None
    
    print(f"🔍 Checking schedules at {now.strftime('%H:%M:%S')}...")
    
    for schedule in st.session_state.schedules:
        if schedule['completed'] or schedule['date'] != today:
            continue
        
        # Calculate time difference
        schedule_datetime = datetime.combine(schedule['date'], schedule['start_time'])
        time_diff_seconds = (schedule_datetime - now).total_seconds()
        time_diff = time_diff_seconds / 60  # in minutes
        
        print(f"  📋 {schedule['title']}: {time_diff:.1f} minutes until start")
        
        # ============================================================
        # MISSED SCHEDULE HANDLING (10 minutes after)
        # ============================================================
        if time_diff < -10:  # More than 10 minutes past start
            notification_id = f"missed_10min_{schedule['id']}"
            
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                print(f"  🚨 MISSED >10min: {schedule['title']}")
                
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': 'missed_10min',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'action': 'auto_block',
                    'message': f"🚨 Missed: {schedule['title']} started {abs(int(time_diff))} minutes ago. Blocking distractions now!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send Windows desktop notification
                if notif_manager and notif_manager.is_available():
                    print(f"  📢 Sending desktop notification (missed_10)...")
                    send_schedule_alert(schedule, 'missed_10')
                else:
                    print(f"  ⚠️ Desktop notifications unavailable")
                
                log_user_activity(
                    ACTIVITY_TYPES['SCHEDULE_MISSED'], 
                    details=f"Missed >10min: {schedule['title']}",
                    metadata={
                        'schedule_id': schedule['id'],
                        'time_missed': abs(int(time_diff))
                    }
                )
                
                schedule['auto_block_triggered'] = True
        
        # ============================================================
        # MISSED SCHEDULE HANDLING (5 minutes after)
        # ============================================================
        elif -10 <= time_diff < -5:
            notification_id = f"missed_5min_{schedule['id']}"
            
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                print(f"  😟 MISSED 5min: {schedule['title']}")
                
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': 'missed_5min',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'action': 'warning',
                    'message': f"😟 Missed: {schedule['title']} started {abs(int(time_diff))} minutes ago. Start now or sites will be blocked!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send Windows desktop notification
                if notif_manager and notif_manager.is_available():
                    print(f"  📢 Sending desktop notification (missed_5)...")
                    send_schedule_alert(schedule, 'missed_5')
                
                log_user_activity(
                    ACTIVITY_TYPES['SCHEDULE_MISSED'], 
                    details=f"Missed 5min: {schedule['title']}",
                    metadata={'schedule_id': schedule['id']}
                )
        
        # ============================================================
        # 10 MINUTES BEFORE
        # ============================================================
        elif 9 <= time_diff <= 11:
            notification_id = f"notif_10min_{schedule['id']}"
            
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                print(f"  ⏰ 10min WARNING: {schedule['title']}")
                
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': '10min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"⏰ Upcoming: {schedule['title']} starts in 10 minutes at {schedule['start_time'].strftime('%H:%M')}"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send Windows desktop notification
                if notif_manager and notif_manager.is_available():
                    print(f"  📢 Sending desktop notification (10min)...")
                    send_schedule_alert(schedule, '10min')
                
                log_user_activity(
                    ACTIVITY_TYPES['NOTIFICATION_SENT'],
                    details=f"10min warning: {schedule['title']}",
                    metadata={'schedule_id': schedule['id']}
                )
        
        # ============================================================
        # 5 MINUTES BEFORE
        # ============================================================
        elif 4 <= time_diff <= 6:
            notification_id = f"notif_5min_{schedule['id']}"
            
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                print(f"  ⚠️ 5min WARNING: {schedule['title']}")
                
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': '5min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"⚠️ Starting Soon: {schedule['title']} in 5 minutes! Get ready! 💪"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send Windows desktop notification
                if notif_manager and notif_manager.is_available():
                    print(f"  📢 Sending desktop notification (5min)...")
                    send_schedule_alert(schedule, '5min')
                
                log_user_activity(
                    ACTIVITY_TYPES['NOTIFICATION_SENT'],
                    details=f"5min warning: {schedule['title']}",
                    metadata={'schedule_id': schedule['id']}
                )
        
        # ============================================================
        # AT START TIME
        # ============================================================
        elif -1 <= time_diff <= 1:
            notification_id = f"notif_start_{schedule['id']}"
            
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                print(f"  🔔 START NOW: {schedule['title']}")
                
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': 'start_now',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"🔔 Starting Now: {schedule['title']}! Time to focus! 🎯"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send Windows desktop notification
                if notif_manager and notif_manager.is_available():
                    print(f"  📢 Sending desktop notification (start)...")
                    send_schedule_alert(schedule, 'start')
                
                log_user_activity(
                    ACTIVITY_TYPES['NOTIFICATION_SENT'],
                    details=f"Start notification: {schedule['title']}",
                    metadata={'schedule_id': schedule['id']}
                )
    
    if new_notifications:
        print(f"✅ Created {len(new_notifications)} new notification(s)")
    
    return new_notifications


def auto_block_for_missed_schedules(blocker):
    """
    Automatically block websites for schedules missed by >10 minutes
    
    Args:
        blocker: WebsiteBlocker instance
    
    Returns:
        dict: Blocking results
    """
    blocked_schedules = []
    
    # Get notification manager for blocking notification
    notif_manager = get_notification_manager() if NOTIFICATIONS_AVAILABLE else None
    
    for schedule in st.session_state.schedules:
        # Check if schedule needs auto-blocking
        if schedule.get('auto_block_triggered') and not schedule.get('auto_blocked'):
            # Check if blocker has admin privileges
            if not blocker._check_admin_privileges():
                schedule['auto_blocked'] = False
                continue
            
            # Block websites
            result = blocker.block_websites(enable_smart_blocking=True)
            
            if result['success']:
                schedule['auto_blocked'] = True
                blocked_schedules.append(schedule['title'])
                
                # Send blocking notification
                if notif_manager and notif_manager.is_available():
                    print(f"📢 Sending blocking notification...")
                    notif_manager.send_blocking_notification(len(result['blocked_sites']))
                
                # Log the auto-blocking
                log_user_activity(
                    ACTIVITY_TYPES['BLOCKING_BY_SCHEDULE'],
                    details=f"Auto-blocked for: {schedule['title']}",
                    metadata={
                        'schedule_id': schedule['id'],
                        'sites_blocked': len(result['blocked_sites'])
                    }
                )
                
                # Mark session state
                st.session_state.blocking_active = True
    
    return {
        'success': len(blocked_schedules) > 0,
        'blocked_schedules': blocked_schedules
    }


def handle_schedule_start(schedule_id):
    """
    Handle when user starts a scheduled task
    Clears missed flags and cancels auto-blocking
    """
    schedule = get_schedule_by_id(schedule_id)
    if schedule:
        schedule['started'] = True
        schedule['auto_block_triggered'] = False
        schedule['missed_notified'] = False
        
        log_user_activity(
            ACTIVITY_TYPES['SCHEDULE_STARTED'],
            details=f"Started: {schedule['title']}",
            metadata={'schedule_id': schedule_id}
        )
        
        return True
    return False


def get_missed_schedules_requiring_block():
    """
    Get list of schedules that require blocking (>10 min missed)
    """
    now = datetime.now()
    today = now.date()
    
    missed_schedules = []
    
    for schedule in st.session_state.schedules:
        if schedule['completed'] or schedule['date'] != today:
            continue
        
        schedule_datetime = datetime.combine(schedule['date'], schedule['start_time'])
        time_diff = (now - schedule_datetime).total_seconds() / 60
        
        # More than 10 minutes past and not started
        if time_diff > 10 and not schedule.get('started') and not schedule.get('auto_blocked'):
            missed_schedules.append({
                'schedule': schedule,
                'minutes_missed': int(time_diff)
            })
    
    return missed_schedules


# Helper function
def get_schedule_by_id(schedule_id):
    """Get a specific schedule by ID"""
    for schedule in st.session_state.schedules:
        if schedule['id'] == schedule_id:
            return schedule
    return None