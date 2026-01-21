# -*- coding: utf-8 -*-
# activity_logger.py
# Complete User Activity Logging System

import csv
import os
from datetime import datetime, timedelta
import json
from pathlib import Path

class ActivityLogger:
    """Log all user activities to CSV file"""
    
    def __init__(self, log_file='user_activity_log.csv'):
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Create log file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'date',
                    'time',
                    'activity_type',
                    'activity_details',
                    'duration_seconds',
                    'success',
                    'metadata'
                ])
    
    def log_activity(self, activity_type, details='', duration=0, success=True, metadata=None):
        """
        Log a user activity
        
        Args:
            activity_type: Type of activity (e.g., 'journal_entry', 'focus_session', 'schedule_created')
            details: Description of the activity
            duration: Duration in seconds (for timed activities)
            success: Whether the activity was successful
            metadata: Additional data as dictionary
        """
        now = datetime.now()
        
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    now.isoformat(),
                    now.strftime('%Y-%m-%d'),
                    now.strftime('%H:%M:%S'),
                    activity_type,
                    details,
                    duration,
                    success,
                    json.dumps(metadata) if metadata else ''
                ])
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_activity_summary(self, days=7):
        """Get summary of activities for the last N days"""
        if not os.path.exists(self.log_file):
            return None
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            activities = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        activity_date = datetime.fromisoformat(row['timestamp']).date()
                        if activity_date >= cutoff_date:
                            activities.append(row)
                    except:
                        continue
            
            return {
                'total_activities': len(activities),
                'activities': activities,
                'by_type': self._group_by_type(activities),
                'by_date': self._group_by_date(activities)
            }
        except Exception as e:
            print(f"Error reading activity log: {e}")
            return None
    
    def _group_by_type(self, activities):
        """Group activities by type"""
        grouped = {}
        for activity in activities:
            activity_type = activity['activity_type']
            if activity_type not in grouped:
                grouped[activity_type] = []
            grouped[activity_type].append(activity)
        return grouped
    
    def _group_by_date(self, activities):
        """Group activities by date"""
        grouped = {}
        for activity in activities:
            date = activity['date']
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(activity)
        return grouped
    
    def export_to_csv(self, filename=None):
        """Export activity log to a new CSV file"""
        if filename is None:
            filename = f"activity_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            # Read all data
            with open(self.log_file, 'r', encoding='utf-8') as source:
                data = source.read()
            
            # Write to new file
            with open(filename, 'w', encoding='utf-8') as dest:
                dest.write(data)
            
            return filename
        except Exception as e:
            print(f"Error exporting log: {e}")
            return None
    
    def clear_old_logs(self, days=30):
        """Clear logs older than specified days"""
        if not os.path.exists(self.log_file):
            return False
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            # Read all activities
            activities = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                for row in reader:
                    try:
                        activity_date = datetime.fromisoformat(row['timestamp']).date()
                        if activity_date >= cutoff_date:
                            activities.append(row)
                    except:
                        continue
            
            # Rewrite file with only recent activities
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(activities)
            
            return True
        except Exception as e:
            print(f"Error clearing old logs: {e}")
            return False


# Activity type constants
ACTIVITY_TYPES = {
    'APP_OPENED': 'app_opened',
    'APP_CLOSED': 'app_closed',
    'PAGE_CHANGED': 'page_changed',
    'JOURNAL_ENTRY': 'journal_entry_created',
    'JOURNAL_ANALYZED': 'journal_entry_analyzed',
    'JOURNAL_DELETED': 'journal_entry_deleted',
    'FOCUS_STARTED': 'focus_session_started',
    'FOCUS_COMPLETED': 'focus_session_completed',
    'FOCUS_CANCELLED': 'focus_session_cancelled',
    'FOCUS_AUTO_COMPLETED': 'focus_session_auto_completed',
    'SCHEDULE_CREATED': 'schedule_created',
    'SCHEDULE_UPDATED': 'schedule_updated',
    'SCHEDULE_COMPLETED': 'schedule_completed',
    'SCHEDULE_DELETED': 'schedule_deleted',
    'SCHEDULE_STARTED': 'schedule_started',
    'SCHEDULE_STARTED_LATE': 'schedule_started_late',
    'SCHEDULE_MISSED': 'schedule_missed',
    'BLOCKING_ENABLED': 'website_blocking_enabled',
    'BLOCKING_DISABLED': 'website_blocking_disabled',
    'BLOCKING_BY_SCHEDULE': 'blocking_enabled_by_schedule',
    'SITE_ADDED': 'blocked_site_added',
    'SITE_REMOVED': 'blocked_site_removed',
    'CAMERA_STARTED': 'camera_monitoring_started',
    'CAMERA_STOPPED': 'camera_monitoring_stopped',
    'DATA_EXPORTED': 'data_exported',
    'DATA_CLEARED': 'data_cleared',
    'NOTIFICATION_SENT': 'notification_sent',
    'SCHEDULE_STARTED': 'schedule_started',
    'SCHEDULE_STARTED_LATE': 'schedule_started_late',
    'SCHEDULE_MISSED': 'schedule_missed',
}


# Helper function to be imported by other modules
def log_user_activity(activity_type, details='', duration=0, success=True, metadata=None):
    """
    Wrapper function to log user activity from any module
    This function can be imported and used throughout the app
    """
    try:
        # This will be called from modules that have access to st.session_state
        import streamlit as st
        
        if 'activity_logger' not in st.session_state:
            st.session_state.activity_logger = ActivityLogger()
        
        return st.session_state.activity_logger.log_activity(
            activity_type=activity_type,
            details=details,
            duration=duration,
            success=success,
            metadata=metadata
        )
    except Exception as e:
        print(f"Activity logging error: {e}")
        return False