import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def render_dashboard(stats_manager, task_manager):
    """Render the main dashboard"""
    st.markdown('<h1 class="main-header">🎓 Your Study Dashboard</h1>', unsafe_allow_html=True)
    
    # Statistics overview
    today_stats = stats_manager.get_today_stats()
    week_stats = stats_manager.get_week_stats()
    streak_info = stats_manager.get_streak_info()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("📅 Today", today_stats['study_time_formatted'], 
                 f"{today_stats['goal_progress']:.0f}% of goal")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("📊 This Week", week_stats['total_formatted'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("🔥 Streak", f"{streak_info['current_streak']} days", 
                 f"Best: {streak_info['longest_streak']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        total_hours = stats_manager.data['total_study_time'] // 3600
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("⏱️ Total Time", f"{total_hours}h")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions and progress
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎯 Quick Start")
        
        if st.button("▶️ Start 25-Min Focus Session", type="primary", use_container_width=True):
            st.session_state.active_page = "⏱️ Focus Timer"
            st.rerun()
        
        if st.button("💝 Check My Emotions", use_container_width=True):
            st.session_state.active_page = "💝 Emotion Check"
            st.rerun()
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.active_page = "📊 Analytics"
            st.rerun()
        
        st.markdown("---")
        
        # Tasks preview
        st.subheader("📝 Today's Tasks")
        pending_tasks = task_manager.get_pending_tasks()
        
        if pending_tasks:
            for task in pending_tasks[:5]:
                priority_emoji = "🔴" if task['priority'] == "High" else "🟡" if task['priority'] == "Normal" else "🟢"
                st.checkbox(
                    f"{priority_emoji} {task['text']}", 
                    key=f"dash_task_{task['id']}",
                    value=task['completed']
                )
        else:
            st.info("No tasks yet. Add some in the Focus Timer tab!")
    
    with col2:
        st.subheader("📈 Weekly Progress")
        
        # Weekly chart
        week_data = week_stats['daily_breakdown']
        df_week = pd.DataFrame(week_data)
        
        fig = px.bar(
            df_week, 
            x='day', 
            y='minutes', 
            title="This Week's Study Time",
            color='minutes',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Minutes"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Motivation quote
    st.markdown("---")
    quote = config.MOTIVATIONAL_QUOTES[datetime.now().day % len(config.MOTIVATIONAL_QUOTES)]
    st.info(f"💡 **Daily Motivation:** {quote}")
    
    # Recent emotion insight
    emotion_insights = stats_manager.get_emotion_insights(7)
    if emotion_insights['total_entries'] > 0:
        st.markdown("---")
        st.subheader("🧠 Recent Emotional State")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Risk", f"{emotion_insights['average_risk']:.0f}/100")
        with col2:
            st.metric("Most Common", emotion_insights['most_common_emotion'].title())
        with col3:
            trend_emoji = "📈" if emotion_insights['trend'] == 'improving' else "📉" if emotion_insights['trend'] == 'declining' else "➡️"
            st.metric("Trend", f"{trend_emoji} {emotion_insights['trend'].title()}")