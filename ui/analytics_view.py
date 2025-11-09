"""
Analytics View UI Component
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def render_analytics(stats_manager):
    """Render the analytics view"""
    st.markdown('<h1 class="main-header">📊 Study Analytics</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Study Time", "💝 Emotions", "🎯 Goals"])
    
    with tab1:
        render_study_time_analytics(stats_manager)
    
    with tab2:
        render_emotion_analytics(stats_manager)
    
    with tab3:
        render_goals_analytics(stats_manager)

def render_study_time_analytics(stats_manager):
    """Render study time analytics"""
    st.subheader("📅 Weekly Study Pattern")
    
    week_stats = stats_manager.get_week_stats()
    df_week = pd.DataFrame(week_stats['daily_breakdown'])
    
    # Weekly bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_week['day'],
        y=df_week['minutes'],
        marker_color='rgb(99, 110, 250)',
        text=df_week['minutes'],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Study Time: %{y} minutes<extra></extra>'
    ))
    
    fig.update_layout(
        title="Daily Study Time This Week",
        xaxis_title="Day",
        yaxis_title="Minutes",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total This Week", week_stats['total_formatted'])
    with col2:
        avg_minutes = week_stats['total_minutes'] // 7
        st.metric("Daily Average", f"{avg_minutes}m")
    with col3:
        most_productive_day = df_week.loc[df_week['minutes'].idxmax(), 'day']
        st.metric("Most Productive", most_productive_day)
    
    st.markdown("---")
    
    # Monthly overview
    st.subheader("📆 Monthly Overview")
    
    daily_sessions = stats_manager.data['daily_sessions']
    last_30_days = []
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
        minutes = daily_sessions.get(date, 0) // 60
        last_30_days.append({'date': date, 'minutes': minutes})
    
    df_month = pd.DataFrame(last_30_days)
    
    fig2 = px.area(
        df_month, 
        x='date', 
        y='minutes', 
        title="Last 30 Days Study Time",
        labels={'date': 'Date', 'minutes': 'Minutes'}
    )
    fig2.update_traces(fill='tozeroy', line_color='rgb(139, 92, 246)')
    fig2.update_layout(height=400)
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Export option
    st.markdown("---")
    if st.button("📥 Export Study Data to CSV"):
        filename = stats_manager.export_to_csv()
        st.success(f"✅ Data exported to: {filename}")

def render_emotion_analytics(stats_manager):
    """Render emotion analytics"""
    st.subheader("🧠 Emotional Insights")
    
    emotion_insights = stats_manager.get_emotion_insights(7)
    
    if emotion_insights['total_entries'] == 0:
        st.info("📝 No emotion data yet. Start checking your emotions to see insights!")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_color = "🔴" if emotion_insights['average_risk'] > 66 else "🟡" if emotion_insights['average_risk'] > 40 else "🟢"
        st.metric("Average Risk", f"{risk_color} {emotion_insights['average_risk']:.0f}/100")
    
    with col2:
        st.metric("Most Common", emotion_insights['most_common_emotion'].title())
    
    with col3:
        trend_emoji = "📈" if emotion_insights['trend'] == 'improving' else "📉" if emotion_insights['trend'] == 'declining' else "➡️"
        st.metric("Trend", f"{trend_emoji} {emotion_insights['trend'].title()}")
    
    st.markdown("---")
    
    # Emotion history chart
    st.subheader("📊 Emotion History")
    
    emotion_history = stats_manager.data['emotion_history'][-14:]
    
    if emotion_history:
        df_emotions = pd.DataFrame([
            {
                'timestamp': datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M'),
                'risk_score': entry['risk_score'],
                'emotion': entry['primary_emotion'].title() if entry['primary_emotion'] else 'Unknown'
            }
            for entry in emotion_history
        ])
        
        fig3 = px.scatter(
            df_emotions, 
            x='timestamp', 
            y='risk_score',
            color='emotion',
            size='risk_score',
            title="Emotion History (Last 14 Entries)",
            labels={'timestamp': 'Time', 'risk_score': 'Risk Score'}
        )
        fig3.update_layout(height=400)
        fig3.add_hline(y=66, line_dash="dash", line_color="red", annotation_text="High Risk")
        fig3.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Moderate Risk")
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Emotion distribution
        st.subheader("🎭 Emotion Distribution")
        
        emotion_counts = df_emotions['emotion'].value_counts()
        fig4 = px.pie(
            values=emotion_counts.values,
            names=emotion_counts.index,
            title="Most Common Emotions"
        )
        fig4.update_layout(height=400)
        
        st.plotly_chart(fig4, use_container_width=True)

def render_goals_analytics(stats_manager):
    """Render goals analytics"""
    st.subheader("🎯 Goal Progress")
    
    today_stats = stats_manager.get_today_stats()
    week_stats = stats_manager.get_week_stats()
    streak_info = stats_manager.get_streak_info()
    
    # Daily goal
    st.markdown("#### 📅 Daily Goal")
    daily_progress = today_stats['goal_progress']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(daily_progress / 100)
    with col2:
        st.metric("Progress", f"{daily_progress:.0f}%")
    
    st.caption(f"{today_stats['study_time_formatted']} / {config.DAILY_GOAL_DEFAULT} minutes")
    
    if daily_progress >= 100:
        st.success("🎉 Daily goal achieved! Great job!")
    elif daily_progress >= 75:
        st.info("💪 Almost there! Keep going!")
    elif daily_progress >= 50:
        st.warning("⚡ Halfway there! You can do it!")
    
    st.markdown("---")
    
    # Weekly goal
    st.markdown("#### 📊 Weekly Goal")
    weekly_progress = week_stats['goal_progress']
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(weekly_progress / 100)
    with col2:
        st.metric("Progress", f"{weekly_progress:.0f}%")
    
    st.caption(f"{week_stats['total_formatted']} / {config.WEEKLY_GOAL_DEFAULT} minutes")
    
    st.markdown("---")
    
    # Streak goal
    st.markdown("#### 🔥 Streak Goal")
    streak_progress = min((streak_info['current_streak'] / streak_info['goal']) * 100, 100)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(streak_progress / 100)
    with col2:
        st.metric("Progress", f"{streak_progress:.0f}%")
    
    st.caption(f"{streak_info['current_streak']} / {streak_info['goal']} days")
    
    if streak_info['current_streak'] >= streak_info['goal']:
        st.balloons()
        st.success(f"🏆 Streak goal achieved! You've studied for {streak_info['current_streak']} consecutive days!")
    
    st.markdown("---")
    
    # Overall statistics
    st.subheader("📈 Overall Statistics")
    
    total_sessions = stats_manager.data['sessions_completed']
    total_time = stats_manager.data['total_study_time']
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sessions", total_sessions)
    
    with col2:
        st.metric("Total Time", f"{total_hours}h {total_minutes}m")
    
    with col3:
        avg_session = (total_time // 60) // total_sessions if total_sessions > 0 else 0
        st.metric("Avg Session", f"{avg_session}m")