# -*- coding: utf-8 -*-
# app2.py
# Main Streamlit Application with Authentication, Website Blocking and Image Emotion Recognition

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time 
from collections import defaultdict

from auth import show_auth_page, logout_user, show_user_profile_sidebar
from profile_page import show_profile_page, show_profile_widget

# Import from config file
from config import (
    MENTAL_HEALTH_MAPPING, MOTIVATIONAL_QUOTES, BLOCKED_SITES, get_custom_css,
    load_model, predict_emotions_multilabel, calculate_risk_score,
    format_time, calculate_study_streak, get_today_focus_time,
    show_website_blocking_warning, show_admin_requirement, initialize_session_state,
    get_today_schedules,  get_unread_notifications,
    get_schedule_stats,
    # Image emotion recognition imports
    get_session_image_emotions, get_image_emotion_summary, 
    get_all_sessions_with_image_data, IMAGE_EMOTION_LABELS
)

# Import activity logger
from activity_logger import ActivityLogger, ACTIVITY_TYPES, log_user_activity

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Perry - Mental Health & Productivity Hub",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ⭐ AUTHENTICATION CHECK - ADD THIS SECTION
# ============================================================================
# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# If not authenticated, show auth page and stop execution
if not st.session_state.authenticated:
    show_auth_page()
    st.stop()

# ============================================================================
# INITIALIZATION (Only runs after authentication)
# ============================================================================
initialize_session_state()

# Initialize activity logger
if 'activity_logger' not in st.session_state:
    st.session_state.activity_logger = ActivityLogger()

# Log app opened
if 'app_session_started' not in st.session_state:
    st.session_state.app_session_started = True
    log_user_activity(ACTIVITY_TYPES['APP_OPENED'], 
                     details=f"App opened at {datetime.now().strftime('%H:%M:%S')}")

# Get the website blocker instance
blocker = st.session_state.website_blocker

# Apply custom CSS based on theme
st.markdown(get_custom_css(st.session_state.dark_mode), unsafe_allow_html=True)

model, tokenizer, emotion_labels = load_model()



# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/mental-health.png", width=100)
    st.title("🎯 Perry - Your Productivity Buddy")
    
    # ⭐ ADD THIS LINE - SHOW USER PROFILE
    show_user_profile_sidebar()
    
    st.markdown("---")
    
    # Dark Mode Toggle
    dark_mode_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key='dark_mode_switch')
    if dark_mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_toggle
        st.rerun()
    
    st.markdown("---")
    
    # Check if quick navigation was triggered
    if 'navigate_to' in st.session_state:
        st.session_state.current_page = st.session_state.navigate_to
        del st.session_state.navigate_to
    
    page = st.radio(
    "Navigation",
    [
        "🏠 Dashboard Overview",
        "👤 My Profile",
        "💬 Talk to Perry",  # ⭐ ADD THIS LINE
        "📝 Journal Analyzer", 
        "⏱️ Focus Timer",
        "📅 Schedule Manager",
        "📊 Analytics & Insights",
        "📈 Productivity Report"
    ],
    index=[
        "🏠 Dashboard Overview",
        "👤 My Profile",
        "💬 Talk to Perry",  # ⭐ ADD THIS LINE
        "📝 Journal Analyzer", 
        "⏱️ Focus Timer",
        "📅 Schedule Manager",
        "📊 Analytics & Insights",
        "📈 Productivity Report"
    ].index(st.session_state.current_page),
    label_visibility="collapsed"
    )
    
    # Track page changes (AFTER page is defined)
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = page
    elif st.session_state.previous_page != page:
        log_user_activity(ACTIVITY_TYPES['PAGE_CHANGED'],
                         details=f"From {st.session_state.previous_page} to {page}")
        st.session_state.previous_page = page
    
    # Update current page
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("📊 Today's Stats")
    today_focus = get_today_focus_time()
    streak = calculate_study_streak()
    today_schedules = len(get_today_schedules())
    unread_notifs = len(get_unread_notifications())
    
    st.metric("Focus Time Today", f"{today_focus} min")
    st.metric("Study Streak", f"{streak} days 🔥")
    st.metric("Today's Tasks", today_schedules)

    # In app2.py sidebar section (after the metrics)

# Enhanced notification display
unread_notifs = get_unread_notifications()

if unread_notifs:
    
    if len(unread_notifs) > 0:
        st.warning(f"🔔 {unread_notifs} notification{'s' if len(unread_notifs) > 1 else ''}")
    
    # Show blocking status in sidebar
    if blocker.is_blocking_active():
        st.markdown('<div class="blocking-active" style="font-size: 0.9rem; padding: 0.8rem;">🚫 Blocking Active</div>', unsafe_allow_html=True)
    
    # Show camera monitoring status in sidebar
    if st.session_state.camera_monitoring:
        st.markdown('<div class="camera-active" style="font-size: 0.9rem; padding: 0.8rem;">📷 Camera Active</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Motivational quote
    quote = np.random.choice(MOTIVATIONAL_QUOTES)
    st.info(f"💬 {quote}")
    
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Settings"):
        # Check admin status
        has_admin = blocker._check_admin_privileges()
        
        if has_admin:
            st.success("✅ Admin privileges detected")
            
            # Manual unblock button
            if blocker.is_blocking_active():
                if st.button("🔓 Unblock All Websites Now"):
                    result = blocker.unblock_websites()
                    if result['success']:
                        st.session_state.blocking_active = False
                        st.success("✅ All websites unblocked!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
        else:
            st.warning("⚠️ No admin privileges - blocking disabled")
        
        # Camera monitoring controls
        st.markdown("---")
        st.write("**📷 Camera Monitoring**")
        
        if st.session_state.camera_monitoring:
            st.warning("⚠️ Camera is currently active")
            if st.button("🔴 Stop Camera Monitoring"):
                recognizer = st.session_state.image_recognizer
                recognizer.stop_monitoring()
                st.session_state.camera_monitoring = False
                st.success("Camera monitoring stopped")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Camera monitoring is inactive")
        
        # Show total emotion captures
        if 'image_emotions' in st.session_state:
            total_captures = len(st.session_state.image_emotions)
            st.caption(f"Total emotions captured: {total_captures}")
        
        # Activity Log Section
        st.markdown("---")
        st.write("**📊 Activity Log**")
        
        if st.button("📥 Export Activity Log"):
            try:
                export_file = st.session_state.activity_logger.export_to_csv()
                if export_file:
                    with open(export_file, 'r') as f:
                        log_data = f.read()
                    
                    st.download_button(
                        label="⬇️ Download Activity Log",
                        data=log_data,
                        file_name=export_file,
                        mime="text/csv"
                    )
                    
                    log_user_activity(ACTIVITY_TYPES['DATA_EXPORTED'],
                                     details="Activity log exported")
                    
                    st.success(f"✅ Activity log ready for download!")
                else:
                    st.error("❌ Failed to export activity log")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Show activity summary
        if st.checkbox("📈 Show Activity Summary"):
            summary = st.session_state.activity_logger.get_activity_summary(days=7)
            
            if summary:
                st.write(f"**Last 7 Days: {summary['total_activities']} activities**")
                
                # By type
                st.write("**By Type:**")
                for activity_type, activities in sorted(summary['by_type'].items(), 
                                                        key=lambda x: len(x[1]), 
                                                        reverse=True)[:10]:
                    st.write(f"• {activity_type}: {len(activities)}")
                
                # By date
                st.write("**By Date:**")
                for date, activities in sorted(summary['by_date'].items(), reverse=True)[:7]:
                    st.write(f"• {date}: {len(activities)} activities")
            else:
                st.info("No activity data available")
        
        # Clear data button
        st.markdown("---")
        if st.button("🗑️ Clear All Data"):
            # Stop camera if running
            if st.session_state.camera_monitoring:
                recognizer = st.session_state.image_recognizer
                recognizer.stop_monitoring()
                st.session_state.camera_monitoring = False
            
            # Log before clearing
            log_user_activity(ACTIVITY_TYPES['DATA_CLEARED'],
                             details="User cleared all app data")
            
            # Export activity log before clearing
            try:
                export_file = st.session_state.activity_logger.export_to_csv(
                    f"activity_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
                if export_file:
                    st.info(f"📁 Activity log backed up to: {export_file}")
            except:
                pass
            
            # Clear all data
            st.session_state.emotion_history = []
            st.session_state.focus_sessions = []
            st.session_state.analysis_count = 0
            st.session_state.image_emotions = []
            st.session_state.schedules = []
            st.session_state.notifications = []
            
            st.success("✅ All data cleared!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    st.caption("ℹ️ Educational project for mental health & productivity support")

# ============================================================================
# IMPORT PAGE MODULES
# ============================================================================
from pages import (
    show_dashboard,
    show_journal_analyzer,
    show_focus_timer,
    show_schedule_manager,
    show_analytics,
    show_productivity_report
)
from TalkToPerry import show_talk_to_perry

# ============================================================================
# ROUTE TO APPROPRIATE PAGE
# ============================================================================
if page == "🏠 Dashboard Overview":
    show_dashboard()
elif page == "👤 My Profile":  # NEW ROUTE
    show_profile_page()
elif page == "💬 Talk to Perry":  # ⭐ ADD THIS ROUTE
    show_talk_to_perry()
elif page == "📝 Journal Analyzer":
    show_journal_analyzer(model, tokenizer, emotion_labels)
elif page == "⏱️ Focus Timer":
    show_focus_timer(blocker)
elif page == "📅 Schedule Manager":
    show_schedule_manager()
elif page == "📊 Analytics & Insights":
    show_analytics()
elif page == "📈 Productivity Report":
    show_productivity_report()

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <h4>🎯 Perry - Your Mental Health & Productivity Buddy</h4>
    <p>Built with ❤️ using Streamlit, RoBERTa & TensorFlow</p>
    <p><small>⚠️ Disclaimer: This is an educational project for personal wellness tracking. 
    For serious mental health concerns, please consult qualified healthcare professionals.</small></p>
    <p><small>🔒 Your data is stored locally and never shared.</small></p>
    <p><small>📷 Camera captures are analyzed and immediately deleted - only emotion predictions are stored.</small></p>
</div>
""", unsafe_allow_html=True)