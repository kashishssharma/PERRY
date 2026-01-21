# Enhanced Notification System with Auto-Blocking
# Add these functions to your config.py or create enhanced_notifications.py

import streamlit as st
from datetime import datetime, timedelta
from collections import defaultdict

# Import your existing systems
try:
    from windows_notifications import get_notification_manager, send_schedule_alert
    DESKTOP_NOTIFICATIONS = True
except:
    DESKTOP_NOTIFICATIONS = False

def check_enhanced_schedule_notifications():
    """
    Enhanced notification system with 10min, 5min, start, missed-5min, missed-10min (auto-block)
    This augments your existing system without replacing it.
    """
    now = datetime.now()
    today = now.date()
    
    # Initialize tracking
    if 'last_notification_check' not in st.session_state:
        st.session_state.last_notification_check = now - timedelta(minutes=1)
    
    # Check every 30 seconds
    time_since_check = (now - st.session_state.last_notification_check).seconds
    if time_since_check < 30:
        return []
    
    st.session_state.last_notification_check = now
    new_notifications = []
    
    # Get notification manager for desktop alerts
    notif_manager = get_notification_manager() if DESKTOP_NOTIFICATIONS else None
    
    for schedule in st.session_state.schedules:
        # Skip completed schedules
        if schedule.get('completed', False):
            continue
        
        # Only check today's schedules
        if schedule['date'] != today:
            continue
        
        schedule_datetime = datetime.combine(schedule['date'], schedule['start_time'])
        time_diff = (schedule_datetime - now).total_seconds() / 60  # minutes
        
        schedule_id = schedule['id']
        schedule_started = schedule.get('started', False)
        
        # ============================================================
        # AUTO-BLOCK: >10 minutes late and not started
        # ============================================================
        if time_diff < -10 and not schedule_started:
            notif_id = f"auto_block_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"🚨 AUTO-BLOCK TRIGGERED: {schedule['title']} ({abs(int(time_diff))}m late)")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'auto_block',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'critical',
                    'auto_block': True,
                    'message': f"🚨 AUTO-BLOCKING: {schedule['title']} missed by {abs(int(time_diff))} minutes!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Mark for auto-blocking
                schedule['auto_block_triggered'] = True
                schedule['auto_block_time'] = now
                
                # Send desktop notification
                if notif_manager and notif_manager.is_available():
                    send_schedule_alert(schedule, 'missed_10')
        
        # ============================================================
        # MISSED 5 MINUTES: 5-10 minutes late and not started
        # ============================================================
        elif -10 < time_diff <= -5 and not schedule_started:
            notif_id = f"missed_5min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"😟 MISSED 5MIN: {schedule['title']} ({abs(int(time_diff))}m late)")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'missed_5min',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'high',
                    'message': f"😟 LATE: {schedule['title']} started {abs(int(time_diff))} minutes ago! Start now or sites will be blocked!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send desktop notification
                if notif_manager and notif_manager.is_available():
                    send_schedule_alert(schedule, 'missed_5')
        
        # ============================================================
        # JUST MISSED: 0-5 minutes late and not started
        # ============================================================
        elif -5 < time_diff < 0 and not schedule_started:
            notif_id = f"just_missed_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"⚠️ JUST MISSED: {schedule['title']} ({abs(int(time_diff))}m late)")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'just_missed',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'medium',
                    'message': f"⚠️ {schedule['title']} started {abs(int(time_diff))} minutes ago!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
        
        # ============================================================
        # 10 MINUTES BEFORE
        # ============================================================
        elif 9 <= time_diff <= 11:
            notif_id = f"10min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"⏰ 10MIN WARNING: {schedule['title']}")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': '10min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'info',
                    'message': f"⏰ Upcoming: {schedule['title']} starts in 10 minutes"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send desktop notification
                if notif_manager and notif_manager.is_available():
                    send_schedule_alert(schedule, '10min')
        
        # ============================================================
        # 5 MINUTES BEFORE
        # ============================================================
        elif 4 <= time_diff <= 6:
            notif_id = f"5min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"⚠️ 5MIN WARNING: {schedule['title']}")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': '5min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'warning',
                    'message': f"⚠️ SOON: {schedule['title']} in 5 minutes! Get ready!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send desktop notification
                if notif_manager and notif_manager.is_available():
                    send_schedule_alert(schedule, '5min')
        
        # ============================================================
        # START TIME (±1 minute)
        # ============================================================
        elif -1 <= time_diff <= 1 and not schedule_started:
            notif_id = f"start_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                print(f"🔔 START NOW: {schedule['title']}")
                
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'start_now',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'severity': 'urgent',
                    'message': f"🔔 START NOW: {schedule['title']}! Click 'Start Task' button!"
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                # Send desktop notification
                if notif_manager and notif_manager.is_available():
                    send_schedule_alert(schedule, 'start')
    
    return new_notifications


def handle_auto_blocking(blocker):
    """
    Execute auto-blocking for schedules missed by >10 minutes
    Call this function in your schedule manager page
    
    Args:
        blocker: Your WebsiteBlocker instance
    
    Returns:
        dict: Results of blocking operation
    """
    blocked_schedules = []
    
    # Get notification manager for blocking notification
    notif_manager = get_notification_manager() if DESKTOP_NOTIFICATIONS else None
    
    for schedule in st.session_state.schedules:
        # Check if auto-blocking is triggered
        if schedule.get('auto_block_triggered') and not schedule.get('auto_blocked'):
            # Verify schedule is still not started
            if schedule.get('started'):
                schedule['auto_block_triggered'] = False
                continue
            
            # Check admin privileges
            if not blocker._check_admin_privileges():
                st.error("🔒 Cannot auto-block: Admin privileges required!")
                schedule['auto_block_triggered'] = False
                continue
            
            # Execute blocking
            print(f"🚫 EXECUTING AUTO-BLOCK for: {schedule['title']}")
            result = blocker.block_websites(enable_smart_blocking=True)
            
            if result['success']:
                schedule['auto_blocked'] = True
                schedule['auto_block_executed'] = datetime.now()
                blocked_schedules.append(schedule['title'])
                
                # Mark blocking as active globally
                st.session_state.blocking_active = True
                st.session_state.blocking_reason = f"Missed schedule: {schedule['title']}"
                
                # Send desktop notification about blocking
                if notif_manager and notif_manager.is_available():
                    notif_manager.send_blocking_notification(len(result['blocked_sites']))
                
                print(f"✅ AUTO-BLOCK SUCCESSFUL: {len(result['blocked_sites'])} sites blocked")
            else:
                print(f"❌ AUTO-BLOCK FAILED: {result['message']}")
                schedule['auto_block_triggered'] = False
    
    return {
        'success': len(blocked_schedules) > 0,
        'blocked_schedules': blocked_schedules,
        'message': f"Auto-blocked for {len(blocked_schedules)} missed schedule(s)"
    }


def show_enhanced_notifications():
    """
    Display notifications with auto-blocking warnings
    Replaces/augments your existing notification display
    """
    unread_notifs = [n for n in st.session_state.notifications if not n.get('read', False)]
    
    if not unread_notifs:
        return
    
    st.markdown("### 🔔 Active Notifications")
    
    # Separate auto-block notifications
    auto_block_notifs = [n for n in unread_notifs if n.get('auto_block', False)]
    other_notifs = [n for n in unread_notifs if not n.get('auto_block', False)]
    
    # Show auto-block notifications first (CRITICAL)
    if auto_block_notifs:
        st.error("🚨 CRITICAL: AUTO-BLOCKING ACTIVE")
        
        for notif in auto_block_notifs:
            with st.container():
                col1, col2, col3 = st.columns([5, 2, 1])
                
                with col1:
                    st.error(f"🚨 **{notif['title']}** - Missed by {abs(int(notif['time_diff']))} minutes!", icon="🚨")
                    st.caption(f"📅 Scheduled: {notif['time'].strftime('%H:%M')} | Sites are being BLOCKED to help you focus!")
                
                with col2:
                    if st.button("▶️ Start Now", key=f"start_block_{notif['id']}", use_container_width=True, type="primary"):
                        # Mark as started
                        for schedule in st.session_state.schedules:
                            if schedule['id'] == notif['schedule_id']:
                                schedule['started'] = True
                                schedule['start_timestamp'] = datetime.now()
                                schedule['auto_block_triggered'] = False
                                break
                        
                        notif['read'] = True
                        st.success(f"✅ Started: {notif['title']}")
                        st.rerun()
                
                with col3:
                    if st.button("✓", key=f"dismiss_block_{notif['id']}", use_container_width=True):
                        notif['read'] = True
                        st.rerun()
        
        st.markdown("---")
    
    # Show other notifications by priority
    if other_notifs:
        severity_order = {'high': 0, 'urgent': 1, 'medium': 2, 'warning': 3, 'info': 4}
        sorted_notifs = sorted(other_notifs, key=lambda n: severity_order.get(n.get('severity', 'info'), 99))
        
        for notif in sorted_notifs:
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 1])
                
                with col1:
                    # Display based on severity
                    if notif['severity'] in ['critical', 'high']:
                        st.error(notif['message'], icon="😟")
                    elif notif['severity'] in ['urgent', 'warning']:
                        st.warning(notif['message'], icon="⚠️")
                    else:
                        st.info(notif['message'], icon="ℹ️")
                    
                    time_ago = (datetime.now() - notif['timestamp']).seconds // 60
                    st.caption(f"📅 {notif['time'].strftime('%H:%M')} | ⏱️ {time_ago}m ago")
                
                with col2:
                    # Show start button for late/starting schedules
                    if notif['type'] in ['missed_5min', 'just_missed', 'start_now']:
                        if st.button("▶️ Start Task", key=f"start_{notif['id']}", use_container_width=True):
                            # Mark schedule as started
                            for schedule in st.session_state.schedules:
                                if schedule['id'] == notif['schedule_id']:
                                    schedule['started'] = True
                                    schedule['start_timestamp'] = datetime.now()
                                    schedule['auto_block_triggered'] = False
                                    break
                            
                            notif['read'] = True
                            st.success(f"✅ Started: {notif['title']}")
                            st.rerun()
                
                with col3:
                    if st.button("✓", key=f"dismiss_{notif['id']}", use_container_width=True):
                        notif['read'] = True
                        st.rerun()
    
    st.markdown("---")


def integrate_enhanced_notifications_to_schedule_manager(blocker):
    """
    INTEGRATION FUNCTION
    Add this at the beginning of your show_schedule_manager() function
    
    Args:
        blocker: Your WebsiteBlocker instance
    """
    # Auto-refresh every 30 seconds
    if 'last_schedule_refresh' not in st.session_state:
        st.session_state.last_schedule_refresh = datetime.now()
    
    time_since_refresh = (datetime.now() - st.session_state.last_schedule_refresh).seconds
    
    # Show countdown
    refresh_in = 30 - time_since_refresh
    if refresh_in > 0:
        st.sidebar.info(f"🔄 Next check in {refresh_in}s")
    
    # Auto-refresh
    if time_since_refresh >= 30:
        st.session_state.last_schedule_refresh = datetime.now()
        st.rerun()
    
    # Check for new notifications
    new_notifications = check_enhanced_schedule_notifications()
    
    # Execute auto-blocking if triggered
    auto_block_result = handle_auto_blocking(blocker)
    
    if auto_block_result['success']:
        st.error(f"🚫 AUTO-BLOCKED: {auto_block_result['message']}")
    
    # Display notifications
    show_enhanced_notifications()


# ============================================================
# USAGE IN YOUR show_schedule_manager() FUNCTION
# ============================================================
"""
Replace the beginning of your show_schedule_manager() with:

def show_schedule_manager():
    st.markdown('<h1 class="main-header">📅 Schedule Manager</h1>', unsafe_allow_html=True)
    
    # Get blocker instance
    blocker = st.session_state.website_blocker
    
    # ADD THIS LINE - integrates everything
    integrate_enhanced_notifications_to_schedule_manager(blocker)
    
    # Rest of your schedule manager code continues...
    tab1, tab2, tab3, tab4 = st.tabs([...])
    # etc...
"""


# ============================================================
# SAVE/LOAD SCHEDULES FOR BACKGROUND SERVICE
# ============================================================
import pickle
import os

def save_schedules_to_file():
    """Save schedules to file for background notification service"""
    import pickle
    try:
        with open('schedules_data.pkl', 'wb') as f:
            pickle.dump(st.session_state.schedules, f)
    except Exception as e:
        print(f"Error saving schedules: {e}")

def load_schedules_from_file():
    """Load schedules from file"""
    try:
        if os.path.exists('schedules_data.pkl'):
            with open('schedules_data.pkl', 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading schedules: {e}")
    return []


# Call this whenever schedules are modified
def sync_schedules():
    """Sync schedules to file for background service"""
    save_schedules_to_file()