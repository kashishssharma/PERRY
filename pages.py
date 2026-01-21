# -*- coding: utf-8 -*-
# pages.py
# All Page Display Functions - COMPLETE FILE WITH BLOCKER INTEGRATION

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time as time_module
from collections import defaultdict

from config import (
    MOTIVATIONAL_QUOTES, predict_emotions_multilabel, calculate_risk_score,
    format_time, calculate_study_streak, get_today_focus_time,
    show_website_blocking_warning, show_admin_requirement,
    check_schedule_conflict, add_schedule, update_schedule, delete_schedule,
    get_schedule_by_id, get_today_schedules, get_upcoming_schedules,
    get_unread_notifications,  # ✅ KEEP ONLY THIS ONE
    get_schedule_stats,
    debug_camera_data,
    # Image emotion recognition
    get_session_image_emotions, get_image_emotion_summary,
    get_all_sessions_with_image_data, IMAGE_EMOTION_LABELS
)

# Add this line after the config imports
from activity_logger import ActivityLogger, ACTIVITY_TYPES, log_user_activity



# ============================================================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================================================
def show_dashboard():
    st.markdown('<h1 class="main-header">🧠 Welcome to Your Mental Health & Productivity Hub</h1>', 
                unsafe_allow_html=True)
    
    # Greeting based on time
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
        emoji = "🌅"
    elif hour < 18:
        greeting = "Good Afternoon"
        emoji = "☀️"
    else:
        greeting = "Good Evening"
        emoji = "🌙"

    st.markdown(f"## {emoji} {greeting}!")

    # Today's overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Journal Entries", len(st.session_state.emotion_history))

    with col2:
        st.metric("⏱️ Focus Sessions", len([s for s in st.session_state.focus_sessions if s['completed']]))

    with col3:
        today_schedules = get_today_schedules()
        completed = sum(1 for s in today_schedules if s['completed'])
        st.metric("📅 Today's Tasks", f"{completed}/{len(today_schedules)}")

    with col4:
        streak = calculate_study_streak()
        st.markdown(f"<div class='streak-badge'>🔥 {streak} Day Streak</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Write Journal Entry", use_container_width=True, key="quick_journal"):
            st.session_state.navigate_to = "📝 Journal Analyzer"
            st.rerun()
    
    with col2:
        if st.button("⏱️ Start Focus Session", use_container_width=True, key="quick_focus"):
            st.session_state.navigate_to = "⏱️ Focus Timer"
            st.rerun()
    
    with col3:
        if st.button("📅 Add Schedule", use_container_width=True, key="quick_schedule"):
            st.session_state.navigate_to = "📅 Schedule Manager"
            st.rerun()
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True, key="quick_analytics"):
            st.session_state.navigate_to = "📊 Analytics & Insights"
            st.rerun()
    
    st.markdown("---")
    
    # Recent activity
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📝 Recent Journal Insights")
        if st.session_state.emotion_history:
            recent_entries = st.session_state.emotion_history[-3:]
            for entry in reversed(recent_entries):
                with st.container():
                    st.markdown(f"**{entry['timestamp'].strftime('%b %d, %H:%M')}**")
                    primary_emotion = entry['emotions'][0]
                    st.write(f"😊 {primary_emotion['emotion'].title()} ({primary_emotion['confidence']*100:.0f}%)")
                    st.caption(f"Risk: {entry['risk_score']:.0f}/100")
                    st.markdown("---")
        else:
            st.info("No journal entries yet. Start writing to track your mental health!")
    
    with col2:
        st.subheader("📅 Today's Schedule")
        today_schedules = get_today_schedules()
        if today_schedules:
            sorted_schedules = sorted(today_schedules, key=lambda x: x['start_time'])[:3]
            for schedule in sorted_schedules:
                with st.container():
                    status = "✅" if schedule['completed'] else "⭕"
                    st.markdown(f"**{status} {schedule['title']}**")
                    st.caption(f"🕐 {schedule['start_time'].strftime('%H:%M')} - {schedule['end_time'].strftime('%H:%M')}")
                    st.caption(f"🏷️ {schedule['category']} • {schedule['priority']}")
                    st.markdown("---")
        else:
            st.info("No schedules for today. Add one to stay organized!")
    
    with col3:
        st.subheader("⏱️ Recent Focus Sessions")
        if st.session_state.focus_sessions:
            recent_sessions = [s for s in st.session_state.focus_sessions if s['completed']][-3:]
            for session in reversed(recent_sessions):
                with st.container():
                    st.markdown(f"**{session['date'].strftime('%b %d, %H:%M')}**")
                    st.write(f"⏱️ Duration: {session['duration']//60} minutes")
                    if session.get('notes'):
                        st.caption(f"📌 {session['notes'][:50]}...")
                    st.markdown("---")
        else:
            st.info("No focus sessions yet. Start a timer to track your productivity!")
    
    # Motivational section
    st.markdown('<div class="quote-box">', unsafe_allow_html=True)
    st.markdown(f"### {np.random.choice(MOTIVATIONAL_QUOTES)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE 2: JOURNAL ANALYZER WITH HISTORY
# ============================================================================
def show_journal_analyzer(model, tokenizer, emotion_labels):
    st.markdown('<h1 class="main-header">📝 Mental Health Journal Analyzer</h1>', unsafe_allow_html=True)
    
    # Create tabs for writing and viewing history
    tab1, tab2 = st.tabs(["✍️ Write New Entry", "📖 View Journal History"])
    
    # TAB 1: Write new entry
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("✍️ Write Your Journal Entry")
            user_input = st.text_area(
                "Share your thoughts, feelings, or experiences...",
                height=200,
                placeholder="Example: Today was challenging. I felt overwhelmed with work and struggled to focus...",
                key="journal_input"
            )
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                analyze_button = st.button("🔍 Analyze Entry", type="primary", use_container_width=True)
            with col_b:
                save_button = st.button("💾 Save Without Analysis", use_container_width=True)
        
        with col2:
            st.subheader("ℹ️ About")
            st.info("""
            **How it helps:**
            
            1. Express your feelings freely
            2. Get AI-powered emotional insights
            3. Track your mental health patterns
            4. Identify concerning trends early
            
            Your privacy is important - all data stays local!
            """)
        
        # Handle save without analysis
        if save_button and user_input:
            entry = {
                'timestamp': datetime.now(),
                'text': user_input,
                'emotions': [{'emotion': 'not_analyzed', 'confidence': 0}],
                'risk_score': 0,
                'analyzed': False
            }
            st.session_state.emotion_history.append(entry)
            st.success("✅ Entry saved successfully!")
            st.info("💡 You can analyze it later from the 'View Journal History' tab")
            time_module.sleep(1)
            st.rerun()
        
        # Handle analyze button
        if analyze_button and user_input:
            with st.spinner("🔄 Analyzing your emotions..."):
                emotions_data = predict_emotions_multilabel(user_input, model, tokenizer, emotion_labels, top_k=5)
                
                if emotions_data:
                    risk_score = calculate_risk_score(emotions_data)
                    
                    # Save entry with analysis
                    entry = {
                        'timestamp': datetime.now(),
                        'text': user_input,
                        'emotions': emotions_data,
                        'risk_score': risk_score,
                        'analyzed': True
                    }
                    st.session_state.emotion_history.append(entry)
                    st.session_state.analysis_count += 1
                    
                    st.markdown("---")
                    st.subheader("🎯 Analysis Results")
                    
                    primary = emotions_data[0]
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Primary Emotion", primary['emotion'].upper(), 
                                 f"{primary['confidence']*100:.1f}%")
                    
                    with col2:
                        risk_color = "🔴" if risk_score > 66 else "🟡" if risk_score > 33 else "🟢"
                        st.metric("Wellness Score", f"{100-risk_score:.0f}/100", risk_color)
                    
                    with col3:
                        st.metric("Total Entries", st.session_state.analysis_count)
                    
                    st.markdown("---")
                    st.subheader("📊 Emotional Breakdown")
                    
                    for emotion in emotions_data:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**{emotion['emotion'].title()}**")
                                st.progress(emotion['confidence'])
                                st.caption(f"💭 {emotion['concern']}")
                            
                            with col2:
                                risk_emoji = "🔴" if emotion['risk_level'] == 'high' else "🟡" if emotion['risk_level'] == 'medium' else "🟢"
                                st.markdown(f"### {risk_emoji}")
                                st.caption(emotion['risk_level'].upper())
                            
                            st.markdown("---")
                    
                    # Supportive feedback
                    st.subheader("💙 Supportive Guidance")
                    
                    if risk_score > 66:
                        st.error("""
                        **We noticed you might be struggling**
                        
                        Your entry shows signs of significant emotional distress. Remember:
                        - 💬 Talking to someone can help - reach out to a friend, family, or professional
                        - 📞 Crisis helplines are available 24/7 if you need immediate support
                        - 🧘 Self-care activities might provide temporary relief
                        
                        You don't have to face this alone. Professional support is available and effective.
                        """)
                    elif risk_score > 33:
                        st.warning("""
                        **Taking care of yourself**
                        
                        Your emotions show some stress or concern. Consider:
                        - 💝 Practice self-compassion and be kind to yourself
                        - 📋 Break tasks into smaller, manageable steps
                        - 👥 Connect with supportive people in your life
                        - 📝 Continue journaling to process your feelings
                        """)
                    else:
                        st.success("""
                        **You're doing great!**
                        
                        Your emotional state appears balanced. Keep it up by:
                        - ✅ Maintaining healthy habits and routines
                        - 🎉 Celebrating your wins, big and small
                        - 📈 Building on your current momentum
                        - 🙏 Practicing gratitude for positive moments
                        """)
                    
                    st.success("✅ Entry saved to your journal!")
    
    # TAB 2: View journal history
    with tab2:
        st.subheader("📖 Your Journal History")
        
        if not st.session_state.emotion_history:
            st.info("📭 No journal entries yet. Write your first entry in the 'Write New Entry' tab!")
        else:
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Entries", len(st.session_state.emotion_history))
            
            with col2:
                analyzed_count = sum(1 for e in st.session_state.emotion_history if e.get('analyzed', False))
                st.metric("Analyzed", analyzed_count)
            
            with col3:
                if analyzed_count > 0:
                    avg_wellness = np.mean([100 - e['risk_score'] for e in st.session_state.emotion_history if e.get('analyzed', False)])
                    st.metric("Avg Wellness", f"{avg_wellness:.0f}/100")
                else:
                    st.metric("Avg Wellness", "N/A")
            
            with col4:
                days_tracked = len(set(e['timestamp'].date() for e in st.session_state.emotion_history))
                st.metric("Days Tracked", days_tracked)
            
            st.markdown("---")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_analyzed = st.selectbox(
                    "Filter by Analysis",
                    ["All Entries", "Analyzed Only", "Not Analyzed"]
                )
            
            with col2:
                sort_order = st.selectbox(
                    "Sort by",
                    ["Newest First", "Oldest First"]
                )
            
            with col3:
                entries_per_page = st.selectbox(
                    "Entries per page",
                    [5, 10, 20, 50],
                    index=1
                )
            
            # Filter entries
            filtered_entries = st.session_state.emotion_history.copy()
            
            if filter_analyzed == "Analyzed Only":
                filtered_entries = [e for e in filtered_entries if e.get('analyzed', False)]
            elif filter_analyzed == "Not Analyzed":
                filtered_entries = [e for e in filtered_entries if not e.get('analyzed', False)]
            
            # Sort entries
            if sort_order == "Newest First":
                filtered_entries = sorted(filtered_entries, key=lambda x: x['timestamp'], reverse=True)
            else:
                filtered_entries = sorted(filtered_entries, key=lambda x: x['timestamp'])
            
            if not filtered_entries:
                st.info("No entries match your filter criteria.")
            else:
                # Pagination
                total_entries = len(filtered_entries)
                total_pages = (total_entries - 1) // entries_per_page + 1
                
                if 'journal_page' not in st.session_state:
                    st.session_state.journal_page = 1
                
                # Page navigation
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("⬅️ Previous", disabled=(st.session_state.journal_page == 1)):
                        st.session_state.journal_page -= 1
                        st.rerun()
                
                with col2:
                    st.markdown(f"<div style='text-align: center;'>Page {st.session_state.journal_page} of {total_pages}</div>", unsafe_allow_html=True)
                
                with col3:
                    if st.button("Next ➡️", disabled=(st.session_state.journal_page == total_pages)):
                        st.session_state.journal_page += 1
                        st.rerun()
                
                st.markdown("---")
                
                # Display entries for current page
                start_idx = (st.session_state.journal_page - 1) * entries_per_page
                end_idx = min(start_idx + entries_per_page, total_entries)
                
                for idx, entry in enumerate(filtered_entries[start_idx:end_idx], start=start_idx + 1):
                    with st.expander(
                        f"Entry #{total_entries - idx + 1} - {entry['timestamp'].strftime('%B %d, %Y at %I:%M %p')}",
                        expanded=False
                    ):
                        # Entry card styling
                        st.markdown('<div class="journal-entry-card">', unsafe_allow_html=True)
                        
                        # Header with date and status
                        st.markdown(f'<span class="journal-entry-date">📅 {entry["timestamp"].strftime("%A, %B %d, %Y")}</span>', unsafe_allow_html=True)
                        st.markdown(f'<span>🕐 {entry["timestamp"].strftime("%I:%M %p")}</span>', unsafe_allow_html=True)
                        
                        # Entry text
                        st.markdown('<div class="journal-entry-text">', unsafe_allow_html=True)
                        st.write(entry['text'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Analysis results if available
                        if entry.get('analyzed', False) and entry['emotions'][0]['emotion'] != 'not_analyzed':
                            st.markdown("---")
                            st.markdown("**🎯 Emotional Analysis:**")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                primary = entry['emotions'][0]
                                st.write(f"**Primary Emotion:** {primary['emotion'].title()}")
                                st.write(f"**Confidence:** {primary['confidence']*100:.1f}%")
                            
                            with col2:
                                wellness = 100 - entry['risk_score']
                                st.write(f"**Wellness Score:** {wellness:.0f}/100")
                                risk_level = "🔴 High" if entry['risk_score'] > 66 else "🟡 Medium" if entry['risk_score'] > 33 else "🟢 Low"
                                st.write(f"**Risk Level:** {risk_level}")
                            
                            # Top emotions
                            st.markdown("**Top Emotions Detected:**")
                            for emotion in entry['emotions'][:3]:
                                st.progress(emotion['confidence'], text=f"{emotion['emotion'].title()} - {emotion['confidence']*100:.0f}%")
                        else:
                            st.info("ℹ️ This entry hasn't been analyzed yet.")
                            if st.button(f"🔍 Analyze Now", key=f"analyze_{idx}"):
                                with st.spinner("Analyzing..."):
                                    emotions_data = predict_emotions_multilabel(entry['text'], model, tokenizer, emotion_labels, top_k=5)
                                    if emotions_data:
                                        entry['emotions'] = emotions_data
                                        entry['risk_score'] = calculate_risk_score(emotions_data)
                                        entry['analyzed'] = True
                                        st.success("✅ Analysis complete!")
                                        st.rerun()
                        
                        # Action buttons
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(f"🗑️ Delete Entry", key=f"delete_{idx}"):
                                st.session_state.emotion_history.remove(entry)
                                st.success("Entry deleted!")
                                st.rerun()
                        
                        with col2:
                            # Export individual entry
                            entry_text = f"Date: {entry['timestamp'].strftime('%Y-%m-%d %H:%M')}\n\n{entry['text']}"
                            st.download_button(
                                label="📥 Export",
                                data=entry_text,
                                file_name=f"journal_entry_{entry['timestamp'].strftime('%Y%m%d_%H%M')}.txt",
                                mime="text/plain",
                                key=f"export_{idx}"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Export all entries
                st.markdown("---")
                if st.button("📥 Export All Entries as CSV"):
                    df_entries = pd.DataFrame([{
                        'Date': e['timestamp'].strftime('%Y-%m-%d'),
                        'Time': e['timestamp'].strftime('%H:%M'),
                        'Entry': e['text'],
                        'Primary_Emotion': e['emotions'][0]['emotion'] if e.get('analyzed') else 'Not Analyzed',
                        'Wellness_Score': f"{100 - e['risk_score']:.0f}" if e.get('analyzed') else 'N/A'
                    } for e in st.session_state.emotion_history])
                    
                    csv = df_entries.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Journal Export",
                        data=csv,
                        file_name=f"journal_history_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

# ============================================================================
# PAGE 3: FOCUS TIMER WITH WEBSITE BLOCKING
# ============================================================================
# Enhanced Focus Timer Section for pages.py
# Add this to replace the existing show_focus_timer function

def show_focus_timer(blocker):
    """Focus timer page with custom blocking and camera monitoring"""
    st.markdown('<h1 class="main-header">⏱ Focus Timer & Study Tracker</h1>', unsafe_allow_html=True)
    
    # Check admin privileges
    has_admin = blocker._check_admin_privileges()
    
    # Show admin warning if no privileges
    if not has_admin:
        show_admin_requirement()
    
    # Timer configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Configure Your Focus Session")
        
        timer_mode = st.selectbox(
            "Choose Timer Mode",
            ["🏅 Pomodoro (25 min)", "⏱ Custom Duration", "📚 Study Session (45 min)", "⚡ Quick Focus (15 min)"]
        )
        
        if "Custom" in timer_mode:
            duration_minutes = st.slider("Duration (minutes)", 5, 120, 25, 5)
        elif "Pomodoro" in timer_mode:
            duration_minutes = 25
        elif "Study Session" in timer_mode:
            duration_minutes = 45
        else:  # Quick Focus
            duration_minutes = 15
        
        session_notes = st.text_input("Session Goal/Notes (optional)", 
                                      placeholder="e.g., Complete chapter 5, Write essay introduction...")
        
        # Website blocking toggle - disabled if no admin
        block_sites = st.checkbox(
            "🚫 Enable distraction blocking during session", 
            value=False,
            disabled=not has_admin,
            help="Requires admin privileges. Blocks social media and entertainment sites at system level."
        )
        
        # Camera monitoring toggle
        enable_camera = st.checkbox(
            "📷 Enable emotion monitoring via camera",
            value=False,
            help="Monitor your emotions during the focus session using your camera. Images are analyzed and immediately deleted."
        )
        
        if block_sites and not has_admin:
            st.warning("⚠ Blocking disabled - restart app with admin privileges to enable.")
    
    with col2:
        st.subheader("📊 Today's Progress")
        today_focus = get_today_focus_time()
        today_sessions = len([s for s in st.session_state.focus_sessions 
                             if s['date'].date() == datetime.now().date() and s['completed']])
        
        st.metric("⏱ Focus Time", f"{today_focus} min")
        st.metric("✅ Sessions", today_sessions)
        
        streak = calculate_study_streak()
        if streak > 0:
            st.markdown(f"<div class='streak-badge'>🔥 {streak} Day Streak!</div>", 
                       unsafe_allow_html=True)
        
        # Show camera status
        if st.session_state.camera_monitoring:
            st.markdown('<div class="camera-active">📷 Camera Active</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # CUSTOM BLOCKING SECTION - Always visible when admin privileges exist
    if has_admin:
        with st.expander("🔧 Customize Blocking List", expanded=False):
            st.write("*Manage which websites to block during focus sessions*")
            
            # Show current blocked sites
            current_blocked = blocker.get_blocked_sites()
            unique_sites = sorted(set([site.replace('www.', '') for site in current_blocked]))
            
            col_display1, col_display2 = st.columns(2)
            
            with col_display1:
                st.write(f"📋 Current Blocklist ({len(unique_sites)} sites)")
                # Show in a scrollable area
                sites_display = "\n".join([f"• {site}" for site in unique_sites[:15]])
                if len(unique_sites) > 15:
                    sites_display += f"\n• ... and {len(unique_sites) - 15} more"
                st.text_area("Blocked Sites", sites_display, height=200, disabled=True, label_visibility="collapsed")
            
            with col_display2:
                st.write("➕ Add Custom Site**")
                custom_site = st.text_input(
                    "Enter website domain",
                    placeholder="example.com",
                    key="custom_site_input",
                    help="Enter just the domain (e.g., reddit.com, not https://reddit.com)"
                )
                
                if st.button("➕ Add to Blocklist", use_container_width=True):
                    if custom_site:
                        # Clean the input
                        site = custom_site.lower().strip()
                        site = site.replace('http://', '').replace('https://', '').replace('/', '').replace('www.', '')
                        
                        if site:
                            blocker.add_site(site)
                            log_user_activity(ACTIVITY_TYPES['SITE_ADDED'],
                                           details=f"Added {site} to blocklist")
                            st.success(f"✅ Added {site} to blocklist!")
                            time_module.sleep(1)
                            st.rerun()
                    else:
                        st.warning("⚠ Please enter a website domain")
                
                st.markdown("---")
                st.write("🗑 Remove Site**")
                
                if unique_sites:
                    site_to_remove = st.selectbox(
                        "Select site to remove",
                        unique_sites,
                        key="remove_site_select"
                    )
                    if st.button("❌ Remove from Blocklist", use_container_width=True):
                        blocker.remove_site(site_to_remove)
                        log_user_activity(ACTIVITY_TYPES['SITE_REMOVED'],
                                       details=f"Removed {site_to_remove} from blocklist")
                        st.success(f"✅ Removed {site_to_remove} from blocklist!")
                        time_module.sleep(1)
                        st.rerun()
                else:
                    st.info("No sites in blocklist")
            
            # Quick add common sites
            st.markdown("---")
            st.write("⚡ Quick Add Common Distractions**")
            
            common_sites = {
                "Social Media": ["tiktok.com", "snapchat.com", "pinterest.com", "linkedin.com"],
                "Entertainment": ["hulu.com", "disneyplus.com", "primevideo.com", "spotify.com"],
                "Gaming": ["steam.com", "epicgames.com", "twitch.tv", "discord.com"],
                "News": ["cnn.com", "bbc.com", "nytimes.com", "reddit.com"]
            }
            
            col1, col2, col3, col4 = st.columns(4)
            
            for idx, (category, sites) in enumerate(common_sites.items()):
                with [col1, col2, col3, col4][idx]:
                    st.write(f"{category}")
                    for site in sites:
                        clean_site = site.replace('www.', '')
                        if clean_site not in [s.replace('www.', '') for s in current_blocked]:
                            if st.button(f"+ {clean_site}", key=f"quick_add_{site}", use_container_width=True):
                                blocker.add_site(site)
                                log_user_activity(ACTIVITY_TYPES['SITE_ADDED'],
                                               details=f"Quick added {site} to blocklist")
                                st.success(f"✅ Added {site}!")
                                time_module.sleep(0.5)
                                st.rerun()
                        else:
                            st.caption(f"✓ {clean_site}")
    
    # Show current blocking status
    if blocker.is_blocking_active():
        show_website_blocking_warning(blocker)
    
    st.markdown("---")
    
    # Timer display and controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Timer display
        if st.session_state.current_session:
            elapsed = int((datetime.now() - st.session_state.session_start_time).total_seconds())
            remaining = max(0, st.session_state.timer_seconds - elapsed)
            
            st.markdown(f'<div class="timer-display">{format_time(remaining)}</div>', 
                       unsafe_allow_html=True)
            
            # Progress bar
            progress = min(1.0, elapsed / st.session_state.timer_seconds) if st.session_state.timer_seconds > 0 else 0
            st.progress(progress)
            
            # Session info
            session_info = f"📌 {st.session_state.current_session.get('notes', 'Focus session in progress...')}"
            if st.session_state.camera_monitoring:
                session_info += " | 📷 Camera monitoring active"
            st.info(session_info)
            
            # Control buttons
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("⏸ Pause", use_container_width=True):
                    st.warning("⏸ Session paused - take a quick break!")
            
            with col_b:
                if st.button("✅ Complete", use_container_width=True, type="primary"):
                    # Get elapsed time
                    elapsed = int((datetime.now() - st.session_state.session_start_time).total_seconds())
                    
                    # ⭐ CRITICAL: Get the session_id that was used
                    session_id = st.session_state.current_session.get('session_id')
                    print(f"🔍 Completing session with ID: {session_id}")
                    
                    # Log activity before completing
                    log_user_activity(ACTIVITY_TYPES['FOCUS_COMPLETED'], 
                                details=f"Completed {elapsed//60} min session",
                                metadata={
                                    'duration': elapsed,
                                    'notes': st.session_state.current_session.get('notes'),
                                    'session_id': session_id
                                })
                    
                    # Stop camera monitoring FIRST and wait for it to save
                    if st.session_state.camera_monitoring:
                        try:
                            recognizer = st.session_state.image_recognizer
                            print(f"🛑 Stopping camera for session: {session_id}")
                            
                            # Stop monitoring
                            recognizer.stop_monitoring()
                            
                            # Wait for thread to finish and save emotions
                            time_module.sleep(2)
                            
                            st.session_state.camera_monitoring = False
                            
                            # ⭐ CRITICAL: Verify with DEBUG info
                            all_emotions = st.session_state.get('image_emotions', [])
                            print(f"📊 Total emotions in state: {len(all_emotions)}")
                            
                            if all_emotions:
                                # Show all unique session IDs
                                unique_ids = set(e.get('session_id', 'N/A') for e in all_emotions)
                                print(f"📊 Unique session IDs in emotions: {unique_ids}")
                                
                                # Count emotions for THIS session
                                captured_emotions = [e for e in all_emotions if e.get('session_id') == session_id]
                                print(f"✅ Found {len(captured_emotions)} emotions for session {session_id}")
                                
                                if len(captured_emotions) == 0:
                                    # Try to find with partial match
                                    print(f"⚠ Trying partial match...")
                                    for e in all_emotions:
                                        e_sid = e.get('session_id', 'N/A')
                                        print(f"   Emotion session_id: {e_sid}")
                            else:
                                captured_emotions = []
                                print("❌ No emotions in session state at all!")
                            
                        except Exception as e:
                            st.warning(f"⚠ Camera stop issue: {str(e)}")
                            captured_emotions = []
                    else:
                        captured_emotions = []
                    
                    # Save completed session
                    session_data = st.session_state.current_session.copy()
                    session_data['completed'] = True
                    session_data['duration'] = elapsed
                    # ⭐ Make sure session_id is preserved
                    session_data['session_id'] = session_id
                    
                    st.session_state.focus_sessions.append(session_data)
                    
                    print(f"✅ Session completed and saved with ID: {session_id}")
                    
                    # Unblock websites if blocking was active
                    if st.session_state.blocking_active:
                        with st.spinner("Unblocking websites..."):
                            result = blocker.unblock_websites()
                            if result['success']:
                                st.success("✅ Websites unblocked!")
                                log_user_activity(ACTIVITY_TYPES['BLOCKING_DISABLED'],
                                            details="Session completed - blocking disabled")
                            else:
                                st.warning(f"⚠ Unblock issue: {result['message']}")
                        st.session_state.blocking_active = False
                    
                    # Reset timer
                    st.session_state.current_session = None
                    st.session_state.timer_running = False
                    st.session_state.session_start_time = None
                    st.session_state.timer_seconds = 0
                    
                    # Clean up active session ID
                    if 'active_session_id' in st.session_state:
                        del st.session_state.active_session_id
                    
                    # Show confirmation with emotion count
                    emotion_count = len(captured_emotions)
                    
                    if emotion_count > 0:
                        st.success(f"🎉 Great work! You focused for {elapsed//60} minutes! 📷 Captured {emotion_count} emotions!")
                    else:
                        st.success(f"🎉 Great work! You focused for {elapsed//60} minutes!")
                        if st.session_state.camera_monitoring:
                            st.info("ℹ Camera was active but no emotions were captured. Make sure your face is visible!")
                    
                    st.balloons()
                    time_module.sleep(1)
                    st.rerun()
            
            with col_c:
                if st.button("❌ Cancel", use_container_width=True):
                    # Log cancellation
                    log_user_activity(ACTIVITY_TYPES['FOCUS_CANCELLED'], 
                                   details=f"Cancelled after {elapsed//60} min",
                                   metadata={
                                       'duration': elapsed,
                                       'notes': st.session_state.current_session.get('notes')
                                   })
                    
                    # Stop camera monitoring if active
                    if st.session_state.camera_monitoring:
                        try:
                            recognizer = st.session_state.image_recognizer
                            recognizer.stop_monitoring()
                            st.session_state.camera_monitoring = False
                        except Exception as e:
                            st.warning(f"⚠ Camera stop issue: {str(e)}")
                    
                    # Unblock websites if blocking was active
                    if st.session_state.blocking_active:
                        blocker.unblock_websites()
                        log_user_activity(ACTIVITY_TYPES['BLOCKING_DISABLED'],
                                       details="Session cancelled - blocking disabled")
                        st.session_state.blocking_active = False
                    
                    st.session_state.current_session = None
                    st.session_state.timer_running = False
                    st.session_state.session_start_time = None
                    st.session_state.timer_seconds = 0
                    st.warning("Session cancelled")
                    time_module.sleep(1)
                    st.rerun()
            
            # Auto-complete when time is up
            if remaining == 0 and st.session_state.timer_running:
                # Stop camera monitoring if active
                if st.session_state.camera_monitoring:
                    try:
                        recognizer = st.session_state.image_recognizer
                        recognizer.stop_monitoring()
                        st.session_state.camera_monitoring = False
                    except Exception as e:
                        st.warning(f"⚠ Camera stop issue: {str(e)}")
                
                st.success("⏰ Time's up! Great focus session!")
                
                # Log completion
                log_user_activity(ACTIVITY_TYPES['FOCUS_AUTO_COMPLETED'], 
                               details=f"Auto-completed {st.session_state.timer_seconds//60} min session",
                               metadata={
                                   'duration': st.session_state.timer_seconds,
                                   'notes': st.session_state.current_session.get('notes')
                               })
                
                session_data = st.session_state.current_session.copy()
                session_data['completed'] = True
                session_data['duration'] = st.session_state.timer_seconds
                st.session_state.focus_sessions.append(session_data)
                
                # Unblock websites if blocking was active
                if st.session_state.blocking_active:
                    blocker.unblock_websites()
                    log_user_activity(ACTIVITY_TYPES['BLOCKING_DISABLED'],
                                   details="Session auto-completed - blocking disabled")
                    st.session_state.blocking_active = False
                
                st.session_state.current_session = None
                st.session_state.timer_running = False
                st.session_state.session_start_time = None
                st.session_state.timer_seconds = 0
                st.balloons()
                time_module.sleep(2)
                st.rerun()
            
            # Auto-refresh every second while timer is running
            if remaining > 0:
                time_module.sleep(0.5)
                st.rerun()
        
        else:
            # No active session - show start button
            st.markdown(f'<div class="timer-display">{format_time(duration_minutes * 60)}</div>', 
                       unsafe_allow_html=True)
            
        if st.button("▶ Start Focus Session", use_container_width=True, type="primary"):
            # Log session start
            log_user_activity(ACTIVITY_TYPES['FOCUS_STARTED'], 
                        details=f"Started {duration_minutes} min session",
                        metadata={
                            'duration_planned': duration_minutes,
                            'notes': session_notes,
                            'blocking_enabled': block_sites,
                            'camera_enabled': enable_camera
                        })
            
            # Try to block websites if requested
            if block_sites and has_admin:
                with st.spinner("🔒 Activating website blocking..."):
                    result = blocker.block_websites(enable_smart_blocking=True)
                
                if result['success']:
                    st.session_state.blocking_active = True
                    st.success(result['message'])
                    log_user_activity(ACTIVITY_TYPES['BLOCKING_ENABLED'],
                                details=f"Blocked {len(result['blocked_sites'])} sites")
                    
                    # Show blocked sites
                    if result.get('blocked_sites'):
                        with st.expander("🚫 Blocked Sites", expanded=False):
                            for site in result['blocked_sites'][:20]:
                                st.write(f"• {site}")
                            if len(result['blocked_sites']) > 20:
                                st.caption(f"... and {len(result['blocked_sites']) - 20} more")
                    
                    st.warning("⚠ Close and reopen your browser for blocking to take full effect!")
                    time_module.sleep(2)
                else:
                    if result.get('requires_admin'):
                        st.error("❌ Admin privileges required for website blocking!")
                    else:
                        st.error(f"❌ Blocking failed: {result['message']}")
                    st.info("ℹ Continuing without website blocking...")
                    time_module.sleep(2)
            
            # ⭐ CRITICAL FIX: Generate session ID ONCE and use it everywhere
            session_id = f"session_{datetime.now().timestamp()}"
            print(f"🆔 Created session ID: {session_id}")
            
            # Start the session with the session_id
            st.session_state.current_session = {
                'date': datetime.now(),
                'duration': duration_minutes * 60,
                'notes': session_notes if session_notes else 'Focus session',
                'completed': False,
                'session_id': session_id  # ⭐ Store it here
            }
            st.session_state.session_start_time = datetime.now()
            st.session_state.timer_seconds = duration_minutes * 60
            st.session_state.timer_running = True
            
            # ⭐ CRITICAL: Store the session_id separately so camera can access it
            st.session_state.active_session_id = session_id
            
            # Start camera monitoring if requested
            if enable_camera:
                try:
                    if hasattr(st.session_state, 'image_recognizer'):
                        recognizer = st.session_state.image_recognizer
                        if recognizer.model is not None:
                            # ⭐ CRITICAL: Pass the SAME session_id to the camera
                            print(f"📷 Starting camera with session ID: {session_id}")
                            if recognizer.start_monitoring(session_id):
                                st.session_state.camera_monitoring = True
                                st.success("📷 Camera monitoring started!")
                                log_user_activity(ACTIVITY_TYPES['CAMERA_STARTED'],
                                            details=f"Session: {session_id}")
                            else:
                                st.warning("⚠ Could not start camera monitoring")
                        else:
                            st.warning("⚠ Emotion recognition model not loaded. Camera monitoring disabled.")
                    else:
                        st.warning("⚠ Image recognizer not initialized. Camera monitoring disabled.")
                except Exception as e:
                    st.error(f"❌ Camera error: {str(e)}")
                    st.info("ℹ Continuing without camera monitoring...")
            
            time_module.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    # Recent sessions history
    st.subheader("📜 Recent Focus Sessions")
    
    if st.session_state.focus_sessions:
        completed_sessions = [s for s in st.session_state.focus_sessions if s['completed']]
        
        if completed_sessions:
            for session in reversed(completed_sessions[-5:]):
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"{session['date'].strftime('%B %d, %Y - %H:%M')}")
                        if session.get('notes'):
                            st.caption(f"📌 {session['notes']}")
                        
                        # Show if session had camera data
                        if session.get('session_id'):
                            session_emotions = get_session_image_emotions(session['session_id'])
                            if session_emotions:
                                st.caption(f"📷 {len(session_emotions)} emotion captures")
                    
                    with col2:
                        st.metric("Duration", f"{session['duration']//60} min")
                    
                    with col3:
                        st.write("✅ Completed")
                    
                    st.markdown("---")
        else:
            st.info("No completed sessions yet. Start your first focus session above!")
    else:
        st.info("No focus sessions yet. Start tracking your productivity now!")


# ============================================================================
# PAGE 4: SCHEDULE MANAGER
# ============================================================================
# Enhanced Schedule Manager UI - Replace show_schedule_manager in pages.py

# Enhanced Schedule Manager with Edit/Reschedule Functionality
# Replace the existing show_schedule_manager function in pages.py with this version

# FIXED SCHEDULE MANAGER - Replace the show_schedule_manager function in pages.py

# COMPLETE SCHEDULE MANAGER WITH AUTO-NOTIFICATIONS
# Replace your show_schedule_manager function in pages.py with this

# Fixed Schedule Manager Implementation
# Replace your show_schedule_manager() function with this version

from streamlit_autorefresh import st_autorefresh
import streamlit as st
from datetime import datetime, timedelta
from collections import defaultdict
import time as time_module

# ============================================================================
# FIXED AUTO-BLOCKING NOTIFICATION SYSTEM
# Replace the notification checking section in show_schedule_manager()
# ============================================================================

def show_schedule_manager():
    """
    Schedule Manager with FIXED auto-blocking:
    - Blocks websites 10 minutes AFTER scheduled time if task not started
    """
    st.markdown('<h1 class="main-header">📅 Schedule Manager</h1>', unsafe_allow_html=True)
    
    # ⭐ DEFINE ALL REQUIRED VARIABLES AT THE VERY START
    now = datetime.now()
    today = now.date()
    blocker = st.session_state.website_blocker
    
    # ⭐ CLEANUP: Remove malformed notifications
    if 'notifications' in st.session_state:
        st.session_state.notifications = [
            n for n in st.session_state.notifications 
            if isinstance(n, dict) and 'id' in n
        ]
    
    # Auto-refresh every 30 seconds
    refresh_count = st_autorefresh(interval=30000, key="schedule_refresh")
    
    if refresh_count > 0:
        st.sidebar.info(f"🔄 Auto-checked {refresh_count} times")
    
    # ============================================================
    # ✅ DISPLAY BLOCKING STATUS AT TOP
    # ============================================================
    if blocker.is_blocking_active():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.error("🚫 **Blocking Active** - Distracting websites are currently blocked", icon="🚫")
            
            if hasattr(st.session_state, 'blocking_reason'):
                st.caption(f"Reason: {st.session_state.blocking_reason}")
        
        with col2:
            if st.button("🔓 Unblock", key="manual_unblock", use_container_width=True):
                result = blocker.unblock_websites()
                if result['success']:
                    st.session_state.blocking_active = False
                    if hasattr(st.session_state, 'blocking_reason'):
                        del st.session_state.blocking_reason
                    
                    # Clear auto-block flags
                    for schedule in st.session_state.schedules:
                        if schedule.get('auto_block_triggered'):
                            schedule['auto_block_triggered'] = False
                            schedule['auto_blocked'] = False
                    
                    st.success("✅ Websites unblocked!")
                    time_module.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
        
        st.markdown("---")
    
    # ============================================================
    # ✅ NOTIFICATION CHECKING AND AUTO-BLOCKING
    # ============================================================
    new_notifications = []
    
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
        
        # AUTO-BLOCK: Exactly 10 minutes late
        if -11 < time_diff <= -10 and not schedule_started and not schedule.get('auto_block_triggered'):
            notif_id = f"auto_block_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'critical',
                    'time': schedule['start_time'],
                    'message': f"🚨 AUTO-BLOCKING: {schedule['title']} missed by 10 minutes! Sites being blocked!",
                    'timestamp': now,
                    'read': False,
                    'auto_block': True
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                schedule['auto_block_triggered'] = True
                schedule['auto_block_time'] = now
                
                if blocker._check_admin_privileges():
                    result = blocker.block_websites(enable_smart_blocking=True)
                    if result['success']:
                        schedule['auto_blocked'] = True
                        st.session_state.blocking_active = True
                        st.session_state.blocking_reason = f"Missed schedule: {schedule['title']}"
                        
                        try:
                            from windows_notifications import send_schedule_alert
                            send_schedule_alert(schedule, 'missed_10')
                        except:
                            pass
        
        # WARNING: 5-10 minutes late
        elif -10 < time_diff <= -5 and not schedule_started:
            notif_id = f"missed_5min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'message': f"😟 WARNING: {schedule['title']} started {abs(int(time_diff))} minutes ago! Start now or sites will be blocked in {int(10 + time_diff)} minutes!",
                    'timestamp': now,
                    'read': False
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
        
        # JUST MISSED: 0-5 minutes late
        elif -5 < time_diff < 0 and not schedule_started:
            notif_id = f"just_missed_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'late',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'message': f"⚠️ {schedule['title']} started {abs(int(time_diff))} minutes ago!",
                    'timestamp': now,
                    'read': False
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
        
        # 10 MINUTES BEFORE
        elif 9 <= time_diff <= 11:
            notif_id = f"10min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'upcoming',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'message': f"⏰ Upcoming: {schedule['title']} in 10 minutes",
                    'timestamp': now,
                    'read': False
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                try:
                    from windows_notifications import send_schedule_alert
                    send_schedule_alert(schedule, '10min')
                except:
                    pass
        
        # 5 MINUTES BEFORE
        elif 4 <= time_diff <= 6:
            notif_id = f"5min_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'soon',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'message': f"⚠️ SOON: {schedule['title']} in 5 minutes!",
                    'timestamp': now,
                    'read': False
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                try:
                    from windows_notifications import send_schedule_alert
                    send_schedule_alert(schedule, '5min')
                except:
                    pass
        
        # START TIME
        elif -1 <= time_diff <= 1 and not schedule_started:
            notif_id = f"start_{schedule_id}"
            
            if not any(n['id'] == notif_id for n in st.session_state.notifications):
                notification = {
                    'id': notif_id,
                    'schedule_id': schedule_id,
                    'title': schedule['title'],
                    'type': 'start',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'message': f"🔔 START NOW: {schedule['title']}!",
                    'timestamp': now,
                    'read': False
                }
                
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                
                try:
                    from windows_notifications import send_schedule_alert
                    send_schedule_alert(schedule, 'start')
                except:
                    pass
    
    # ============================================================
    # ✅ DISPLAY NOTIFICATIONS
    # ============================================================
    unread_notifs = [n for n in st.session_state.notifications if not n.get('read', False)]
    
    if unread_notifs:
        st.subheader("🔔 Active Notifications")
        
        type_priority = {'critical': 0, 'warning': 1, 'late': 2, 'start': 3, 'soon': 4, 'upcoming': 5}
        sorted_notifs = sorted(unread_notifs, key=lambda n: type_priority.get(n.get('type', 'upcoming'), 99))
        
        for notif in sorted_notifs:
            if not isinstance(notif, dict):
                continue
                
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 1])
                
                with col1:
                    try:
                        message = notif.get('message', f"📌 {notif.get('title', 'Task')}")
                        notif_type = notif.get('type', 'info')
                        
                        if notif_type == 'critical':
                            st.error(message, icon="🚨")
                        elif notif_type in ['warning', 'late']:
                            st.warning(message, icon="⚠️")
                        elif notif_type == 'start':
                            st.warning(message, icon="🔔")
                        elif notif_type == 'soon':
                            st.info(message, icon="⚠️")
                        else:
                            st.info(message, icon="⏰")
                        
                        if 'time' in notif:
                            try:
                                time_ago = (now - notif.get('timestamp', now)).seconds // 60
                                time_str = notif['time'].strftime('%H:%M') if hasattr(notif['time'], 'strftime') else str(notif['time'])
                                st.caption(f"📅 Scheduled: {time_str} | ⏱️ {time_ago}m ago")
                            except:
                                pass
                    
                    except Exception as e:
                        st.info(f"📌 Notification for: {notif.get('title', 'Unknown task')}")
                
                with col2:
                    if notif.get('type') in ['critical', 'warning', 'late', 'start']:
                        if st.button("▶️ Start", key=f"start_{notif['id']}", use_container_width=True):
                            for schedule in st.session_state.schedules:
                                if schedule['id'] == notif.get('schedule_id'):
                                    schedule['started'] = True
                                    schedule['start_timestamp'] = now
                                    schedule['auto_block_triggered'] = False
                                    break
                            
                            notif['read'] = True
                            
                            if notif.get('auto_block'):
                                st.success(f"✅ Started: {notif.get('title')} - Sites remain blocked until completion!")
                            else:
                                st.success(f"✅ Started: {notif.get('title')}")
                            
                            time_module.sleep(0.5)
                            st.rerun()
                
                with col3:
                    if st.button("✓", key=f"dismiss_{notif['id']}", use_container_width=True):
                        notif['read'] = True
                        st.rerun()
        
        st.markdown("---")
    
    # ============================================================
    # TABS FOR SCHEDULE MANAGEMENT
    # ============================================================
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Schedule", "📋 Today's Schedule", "📆 Upcoming", "📊 Statistics"])
    
    # ... rest of your tabs code ...
    # TAB 1: Add New Schedule
    with tab1:
        st.subheader("➕ Create New Schedule")
        
        with st.form("add_schedule_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input(
                    "📌 Task Title*", 
                    placeholder="e.g., Team Meeting, Study Session",
                    key="title_input"
                )
                description = st.text_area(
                    "📝 Description", 
                    placeholder="Optional: Add details about this task",
                    key="desc_input"
                )
                
                category = st.selectbox(
                    "🏷️ Category",
                    ["Work", "Study", "Personal", "Health", "Meeting", "Break", "Other"],
                    key="cat_input"
                )
            
            with col2:
                schedule_date = st.date_input(
                    "📅 Date*", 
                    min_value=datetime.now().date(),
                    key="date_input"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    start_time = st.time_input(
                        "⏰ Start Time*", 
                        value=datetime.now().replace(minute=0, second=0, microsecond=0).time(),
                        key="start_input"
                    )
                
                with col_b:
                    end_time = st.time_input(
                        "⏰ End Time*", 
                        value=(datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).time(),
                        key="end_input"
                    )
                
                priority = st.select_slider(
                    "⚡ Priority",
                    options=["Low", "Medium", "High", "Urgent"],
                    value="Medium",
                    key="priority_input"
                )
            
            st.markdown("---")
            
            submit_button = st.form_submit_button("➕ Add Schedule", type="primary", use_container_width=True)
        
        # Handle form submission
        if submit_button:
            from config import add_schedule, check_schedule_conflict
            
            if not title:
                st.error("❌ Please enter a task title!")
            elif end_time <= start_time:
                st.error("❌ End time must be after start time!")
            else:
                conflicts = check_schedule_conflict(start_time, end_time, schedule_date)
                if conflicts:
                    st.error("❌ This time slot conflicts with existing schedules!")
                    for conflict in conflicts:
                        st.warning(f"⚠️ **{conflict['title']}** ({conflict['start_time'].strftime('%H:%M')} - {conflict['end_time'].strftime('%H:%M')})")
                else:
                    schedule_id = add_schedule(
                        title=title,
                        description=description,
                        date=schedule_date,
                        start_time=start_time,
                        end_time=end_time,
                        category=category,
                        priority=priority
                    )
                    st.success(f"✅ Schedule '{title}' added successfully!")
                    st.balloons()
                    time_module.sleep(1)
                    st.rerun()
    
    # TAB 2: Today's Schedule
    # TAB 2: Today's Schedule
    with tab2:
        from config import get_today_schedules, update_schedule, delete_schedule
    
        st.subheader("📋 Today's Tasks")
    
        today_schedules = sorted(get_today_schedules(), key=lambda x: x['start_time'])
    
        if not today_schedules:
            st.info("🔭 No schedules for today. Add one to get started!")
        else:
        # Progress
            completed_count = sum(1 for s in today_schedules if s['completed'])
            st.metric("Progress", f"{completed_count}/{len(today_schedules)} completed")
            st.progress(completed_count / len(today_schedules) if len(today_schedules) > 0 else 0)
        
            st.markdown("---")
        
        # Display schedules with status
            for schedule in today_schedules:
            # Determine status
                schedule_time = datetime.combine(today, schedule['start_time'])
                time_to_start = (schedule_time - now).total_seconds() / 60
            
                if schedule['completed']:
                    status_icon = "✅"
                    status_text = "Completed"
                elif schedule.get('started'):
                    status_icon = "🔴"
                    status_text = "In Progress"
                elif time_to_start < -10:
                    status_icon = "❌"
                    status_text = "Missed"
                elif time_to_start < 0:
                    status_icon = "😟"
                    status_text = "Late"
                else:
                    status_icon = "⏳"
                    status_text = "Scheduled"
            
                with st.expander(
                    f"{status_icon} {schedule['title']} ({schedule['start_time'].strftime('%H:%M')} - {schedule['end_time'].strftime('%H:%M')}) - {status_text}",
                    expanded=not schedule['completed'] and status_icon in ["❌", "😟", "🔴"]
                ):
                    col1, col2, col3 = st.columns([2, 1, 1])
                
                    with col1:
                        st.write(f"**Category:** {schedule['category']}")
                        st.write(f"**Priority:** {schedule['priority']}")
                        if schedule['description']:
                            st.write(f"**Details:** {schedule['description']}")
                    
                        if schedule.get('start_timestamp'):
                            st.caption(f"▶️ Started: {schedule['start_timestamp'].strftime('%H:%M')}")
                
                    with col2:
                        duration = datetime.combine(datetime.min, schedule['end_time']) - datetime.combine(datetime.min, schedule['start_time'])
                        st.metric("Duration", f"{duration.seconds // 60} min")
                    
                        if time_to_start > 0:
                            st.info(f"Starts in {int(time_to_start)} min")
                        elif time_to_start < 0 and not schedule.get('started'):
                            st.warning(f"Late by {abs(int(time_to_start))} min")
                
                    with col3:
                        if not schedule['completed']:
                            if not schedule.get('started'):
                                if st.button("▶️ Start", key=f"start_sched_{schedule['id']}", use_container_width=True):
                                    schedule['started'] = True
                                    schedule['start_timestamp'] = now
                                    schedule['auto_block_triggered'] = False
                                    st.success("Started!")
                                    time_module.sleep(0.5)
                                    st.rerun()
                        
                            if st.button("✓ Complete", key=f"complete_{schedule['id']}", use_container_width=True):
                                # Mark as completed
                                update_schedule(schedule['id'], completed=True)
                                
                                # ⭐ CHECK IF THIS WAS AN AUTO-BLOCKED SCHEDULE
                                if schedule.get('auto_blocked') and blocker.is_blocking_active():
                                    # Unblock websites since task is completed
                                    result = blocker.unblock_websites()
                                    if result['success']:
                                        st.session_state.blocking_active = False
                                        if hasattr(st.session_state, 'blocking_reason'):
                                            del st.session_state.blocking_reason
                                        
                                        # Clear auto-block flags for all schedules
                                        for s in st.session_state.schedules:
                                            if s.get('auto_block_triggered'):
                                                s['auto_block_triggered'] = False
                                                s['auto_blocked'] = False
                                        
                                        st.success("✅ Task completed! Websites unblocked!")
                                    else:
                                        st.success("✅ Task completed!")
                                        st.warning("⚠️ Could not unblock websites automatically")
                                else:
                                    st.success("✅ Task completed!")
                                
                                time_module.sleep(0.5)
                                st.rerun()
                    
                    # ⭐ ADD EDIT BUTTON HERE
                        if st.button("✏️ Edit", key=f"edit_{schedule['id']}", use_container_width=True):
                            st.session_state[f'editing_{schedule["id"]}'] = True
                            st.rerun()

                        if st.button("🗑️ Delete", key=f"del_{schedule['id']}", use_container_width=True):
                            delete_schedule(schedule['id'])
                            st.rerun()
                
                # ⭐ ADD EDIT FORM HERE
                    if st.session_state.get(f'editing_{schedule["id"]}', False):
                        st.markdown("---")
                        st.subheader("✏️ Edit Schedule")
                    
                        with st.form(f"edit_form_{schedule['id']}"):
                            col_a, col_b = st.columns(2)
                        
                            with col_a:
                                new_title = st.text_input("📌 Task Title", value=schedule['title'])
                                new_description = st.text_area("📝 Description", value=schedule.get('description', ''))
                                new_category = st.selectbox(
                                    "🏷️ Category",
                                    ["Work", "Study", "Personal", "Health", "Meeting", "Break", "Other"],
                                    index=["Work", "Study", "Personal", "Health", "Meeting", "Break", "Other"].index(schedule['category'])
                                )
                        
                            with col_b:
                                new_start_time = st.time_input("⏰ Start Time", value=schedule['start_time'])
                                new_end_time = st.time_input("⏰ End Time", value=schedule['end_time'])
                                new_priority = st.select_slider(
                                    "⚡ Priority",
                                    options=["Low", "Medium", "High", "Urgent"],
                                    value=schedule['priority']
                                )
                        
                            col_submit, col_cancel = st.columns(2)
                        
                            with col_submit:
                                submit_edit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                        
                            with col_cancel:
                                cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                        if submit_edit:
                            from config import check_schedule_conflict
                        
                            if not new_title:
                                st.error("❌ Please enter a task title!")
                            elif new_end_time <= new_start_time:
                                st.error("❌ End time must be after start time!")
                            else:
                                conflicts = check_schedule_conflict(new_start_time, new_end_time, schedule['date'], exclude_id=schedule['id'])
                                if conflicts:
                                    st.error("❌ This time slot conflicts with existing schedules!")
                                    for conflict in conflicts:
                                        st.warning(f"⚠️ **{conflict['title']}** ({conflict['start_time'].strftime('%H:%M')} - {conflict['end_time'].strftime('%H:%M')})")
                                else:
                                    update_schedule(
                                        schedule['id'],
                                        title=new_title,
                                        description=new_description,
                                        start_time=new_start_time,
                                        end_time=new_end_time,
                                        category=new_category,
                                        priority=new_priority
                                    )
                                    del st.session_state[f'editing_{schedule["id"]}']
                                    st.success("✅ Schedule updated successfully!")
                                    time_module.sleep(1)
                                    st.rerun()
                    
                        if cancel_edit:
                            del st.session_state[f'editing_{schedule["id"]}']
                            st.rerun()
    
    # TAB 3: Upcoming Schedules
    with tab3:
        from config import get_upcoming_schedules
        
        st.subheader("📆 Next 7 Days")
        
        upcoming = get_upcoming_schedules(days=7)
        
        if not upcoming:
            st.info("🔭 No upcoming schedules in the next 7 days.")
        else:
            # Group by date
            by_date = defaultdict(list)
            for schedule in upcoming:
                by_date[schedule['date']].append(schedule)
            
            for date in sorted(by_date.keys()):
                schedules = sorted(by_date[date], key=lambda x: x['start_time'])
                
                with st.expander(
                    f"📅 {date.strftime('%A, %B %d, %Y')} ({len(schedules)} task{'s' if len(schedules) > 1 else ''})",
                    expanded=(date == datetime.now().date())
                ):
                    for schedule in schedules:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            status = "✅" if schedule['completed'] else "⏳"
                            st.write(f"{status} **{schedule['title']}**")
                            st.caption(f"{schedule['category']} · {schedule['priority']} priority")
                            st.caption(f"⏰ {schedule['start_time'].strftime('%H:%M')} - {schedule['end_time'].strftime('%H:%M')}")
                        
                        with col2:
                            if not schedule['completed']:
                                if st.button("✓", key=f"complete_upcoming_{schedule['id']}", use_container_width=True):
                                    from config import update_schedule
                                    update_schedule(schedule['id'], completed=True)
                                    st.rerun()
                        
                        st.markdown("---")
    
    # TAB 4: Statistics
    with tab4:
        from config import get_schedule_stats
        
        st.subheader("📊 Schedule Statistics")
        
        stats = get_schedule_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Schedules", stats['total'])
        
        with col2:
            st.metric("Completed", stats['completed'])
        
        with col3:
            st.metric("Pending", stats['pending'])
        
        with col4:
            st.metric("Today", stats['today'])
        
        if stats['total'] > 0:
            st.markdown("---")
            
            # Category and Priority charts
            import plotly.express as px
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 By Category")
                category_counts = defaultdict(int)
                for schedule in st.session_state.schedules:
                    category_counts[schedule['category']] += 1
                
                if category_counts:
                    fig_category = px.pie(
                        values=list(category_counts.values()),
                        names=list(category_counts.keys()),
                        title="Schedule Distribution by Category"
                    )
                    st.plotly_chart(fig_category, use_container_width=True)
            
            with col2:
                st.subheader("⚡ By Priority")
                priority_counts = defaultdict(int)
                for schedule in st.session_state.schedules:
                    priority_counts[schedule['priority']] += 1
                
                if priority_counts:
                    fig_priority = px.bar(
                        x=list(priority_counts.keys()),
                        y=list(priority_counts.values()),
                        labels={'x': 'Priority', 'y': 'Count'},
                        title="Schedule Distribution by Priority"
                    )
                    st.plotly_chart(fig_priority, use_container_width=True)

# ============================================================================
# PAGE 5: ANALYTICS & INSIGHTS
# ============================================================================
def show_analytics():
    st.markdown('<h1 class="main-header">📊 Comprehensive Analytics & Insights</h1>', unsafe_allow_html=True)
    
    if len(st.session_state.emotion_history) == 0 and len(st.session_state.focus_sessions) == 0:
        st.info("ℹ Start using the Journal Analyzer and Focus Timer to see your analytics here!")
    else:
        # Tabs for different analytics
        tab1, tab2, tab3 = st.tabs(["💚 Mental Health Insights", "⏱ Productivity Analytics", "🔗 Combined View"])
        
        # TAB 1: Mental Health Analytics
        with tab1:
            if st.session_state.emotion_history:
                st.subheader("🧠 Mental Health Overview")
                
                # Overall stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Entries", len(st.session_state.emotion_history))
                
                with col2:
                    avg_risk = np.mean([e['risk_score'] for e in st.session_state.emotion_history])
                    wellness_score = 100 - avg_risk
                    st.metric("Avg Wellness", f"{wellness_score:.0f}/100")
                
                with col3:
                    all_emotions = [e['emotions'][0]['emotion'] for e in st.session_state.emotion_history]
                    unique_emotions = len(set(all_emotions))
                    st.metric("Emotions Detected", unique_emotions)
                
                with col4:
                    high_risk_count = sum(1 for e in st.session_state.emotion_history if e['risk_score'] > 66)
                    st.metric("High Risk Days", high_risk_count)
                
                st.markdown("---")
                
                # Emotion trends
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Wellness Score Trend")
                    timestamps = [entry['timestamp'] for entry in st.session_state.emotion_history]
                    wellness_scores = [100 - entry['risk_score'] for entry in st.session_state.emotion_history]
                    
                    fig_wellness = go.Figure()
                    fig_wellness.add_trace(go.Scatter(
                        x=timestamps,
                        y=wellness_scores,
                        mode='lines+markers',
                        name='Wellness Score',
                        line=dict(color='#667eea', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(102, 126, 234, 0.2)'
                    ))
                    fig_wellness.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Wellness Score (0-100)",
                        height=350,
                        yaxis=dict(range=[0, 100])
                    )
                    st.plotly_chart(fig_wellness, use_container_width=True)
                
                with col2:
                    st.subheader("🎭 Emotion Distribution")
                    primary_emotions = [e['emotions'][0]['emotion'] for e in st.session_state.emotion_history]
                    emotion_counts = pd.Series(primary_emotions).value_counts().head(8)
                    
                    fig_emotions = px.bar(
                        x=emotion_counts.values,
                        y=emotion_counts.index,
                        orientation='h',
                        labels={'x': 'Count', 'y': 'Emotion'},
                        color=emotion_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    fig_emotions.update_layout(showlegend=False, height=350)
                    st.plotly_chart(fig_emotions, use_container_width=True)
                
                # Pattern detection and recommendations
                st.subheader("🔍 Pattern Detection")
                
                recent_entries = st.session_state.emotion_history[-7:] if len(st.session_state.emotion_history) >= 7 else st.session_state.emotion_history
                recent_wellness = [100 - e['risk_score'] for e in recent_entries]
                avg_recent_wellness = np.mean(recent_wellness)
                
                positive_emotions = ['joy', 'gratitude', 'love', 'excitement', 'optimism', 'pride']
                recent_positive_count = sum(1 for e in recent_entries if e['emotions'][0]['emotion'] in positive_emotions)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    trend_icon = "📈" if len(recent_wellness) > 1 and recent_wellness[-1] > recent_wellness[0] else "📉"
                    st.metric("Recent Trend", "Improving" if trend_icon == "📈" else "Declining", trend_icon)
                
                with col2:
                    st.metric("Positive Emotions", f"{recent_positive_count}/{len(recent_entries)}")
                
                with col3:
                    consistency = "High" if max(recent_wellness) - min(recent_wellness) < 30 else "Variable"
                    st.metric("Emotional Stability", consistency)
                
                # Recommendations
                if avg_recent_wellness < 50:
                    st.warning("""
                    **💙 Wellness Alert**
                    
                    Your recent entries show lower wellness scores. Consider:
                    - 🧘 Practicing mindfulness or meditation
                    - 💬 Talking to someone you trust
                    - 🏃 Engaging in physical activity
                    - 📞 Reaching out for professional support if needed
                    """)
                else:
                    st.success("""
                    **🎉 Great Progress!**
                    
                    Your wellness scores look positive. Keep it up by:
                    - ✅ Maintaining your current self-care routines
                    - 💪 Building on healthy habits
                    - 🙏 Practicing gratitude regularly
                    """)
            else:
                st.info("No journal entries yet. Start writing to see mental health analytics!")
        
        # TAB 2: Productivity Analytics
        with tab2:
            if st.session_state.focus_sessions:
                completed = [s for s in st.session_state.focus_sessions if s['completed']]
                
                if completed:
                    st.subheader("⏱ Productivity Overview")
                    
                    # Stats
                    total_minutes = sum(s['duration'] for s in completed) // 60
                    total_sessions = len(completed)
                    avg_session = total_minutes // total_sessions if total_sessions > 0 else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Focus Time", f"{total_minutes} min")
                    
                    with col2:
                        st.metric("Total Sessions", total_sessions)
                    
                    with col3:
                        st.metric("Avg Session", f"{avg_session} min")
                    
                    with col4:
                        streak = calculate_study_streak()
                        st.metric("Current Streak", f"{streak} days 🔥")
                    
                    st.markdown("---")
                    
                    # Charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📅 Daily Focus Time")
                        
                        # Group by date
                        daily_data = defaultdict(int)
                        for session in completed:
                            date = session['date'].date()
                            daily_data[date] += session['duration'] // 60
                        
                        dates = sorted(daily_data.keys())
                        minutes = [daily_data[d] for d in dates]
                        
                        fig_daily = go.Figure()
                        fig_daily.add_trace(go.Bar(
                            x=dates,
                            y=minutes,
                            marker_color='#667eea',
                            name='Focus Time'
                        ))
                        fig_daily.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Minutes",
                            height=350
                        )
                        st.plotly_chart(fig_daily, use_container_width=True)
                    
                    with col2:
                        st.subheader("⏱ Session Duration Distribution")
                        
                        durations = [s['duration'] // 60 for s in completed]
                        fig_duration = go.Figure(data=[go.Histogram(
                            x=durations,
                            nbinsx=10,
                            marker_color='#764ba2'
                        )])
                        fig_duration.update_layout(
                            xaxis_title="Duration (minutes)",
                            yaxis_title="Count",
                            height=350
                        )
                        st.plotly_chart(fig_duration, use_container_width=True)
                    
                    # Weekly summary with insights
                    st.subheader("📊 Weekly Summary")
                    
                    today = datetime.now().date()
                    week_start = today - timedelta(days=today.weekday())
                    week_sessions = [s for s in completed if s['date'].date() >= week_start]
                    week_minutes = sum(s['duration'] for s in week_sessions) // 60
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("This Week", f"{week_minutes} min")
                    
                    with col2:
                        st.metric("Sessions", len(week_sessions))
                    
                    with col3:
                        goal = 300  # 5 hours per week
                        progress = min(100, (week_minutes / goal) * 100)
                        st.metric("Weekly Goal", f"{progress:.0f}%")
                    
                    st.progress(progress / 100)
                    
                    st.markdown("---")
                    st.subheader("💡 Productivity Insights")
                    
                    if week_minutes >= 300:
                        st.success("🎉 Amazing! You've hit your weekly focus goal!")
                    elif week_minutes >= 150:
                        st.info(f"👍 Good progress! {300-week_minutes} more minutes to reach your weekly goal.")
                    else:
                        st.warning(f"💪 You can do it! {300-week_minutes} minutes left to achieve this week's goal.")
                else:
                    st.info("Complete your first focus session to see productivity analytics!")
            else:
                st.info("No focus sessions yet. Start tracking your productivity!")
        
        # TAB 3: Combined View
        with tab3:
            st.subheader("🔗 Mental Health & Productivity Correlation")
            
            if st.session_state.emotion_history and st.session_state.focus_sessions:
                # Combine data by date
                combined_data = defaultdict(lambda: {'wellness': [], 'focus_minutes': 0})
                
                for entry in st.session_state.emotion_history:
                    date = entry['timestamp'].date()
                    wellness = 100 - entry['risk_score']
                    combined_data[date]['wellness'].append(wellness)
                
                for session in st.session_state.focus_sessions:
                    if session['completed']:
                        date = session['date'].date()
                        combined_data[date]['focus_minutes'] += session['duration'] // 60
                
                # Prepare for plotting
                dates = sorted(combined_data.keys())
                avg_wellness = [np.mean(combined_data[d]['wellness']) if combined_data[d]['wellness'] else 0 for d in dates]
                focus_mins = [combined_data[d]['focus_minutes'] for d in dates]
                
                if dates:
                    # Dual-axis chart
                    fig_combined = go.Figure()
                    
                    fig_combined.add_trace(go.Scatter(
                        x=dates,
                        y=avg_wellness,
                        name='Wellness Score',
                        yaxis='y',
                        line=dict(color='#667eea', width=3),
                        mode='lines+markers'
                    ))
                    
                    fig_combined.add_trace(go.Bar(
                        x=dates,
                        y=focus_mins,
                        name='Focus Time (min)',
                        yaxis='y2',
                        marker_color='rgba(118, 75, 162, 0.6)'
                    ))
                    
                    fig_combined.update_layout(
                        title="Wellness Score vs Productivity",
                        xaxis=dict(title="Date"),
                        yaxis=dict(
                            title="Wellness Score",
                            side='left',
                            range=[0, 100]
                        ),
                        yaxis2=dict(
                            title="Focus Time (minutes)",
                            side='right',
                            overlaying='y'
                        ),
                        height=400,
                        legend=dict(x=0.01, y=0.99)
                    )
                    
                    st.plotly_chart(fig_combined, use_container_width=True)
                    
                    # Correlation insights
                    st.markdown("---")
                    st.subheader("💡 Insights")
                    
                    # Calculate simple correlation if enough data
                    if len(dates) >= 3:
                        valid_data = [(w, f) for w, f in zip(avg_wellness, focus_mins) if w > 0 and f > 0]
                        
                        if len(valid_data) >= 3:
                            wellness_vals = [d[0] for d in valid_data]
                            focus_vals = [d[1] for d in valid_data]
                            
                            correlation = np.corrcoef(wellness_vals, focus_vals)[0, 1]
                            
                            if correlation > 0.3:
                                st.success(f"""
                                **Positive Correlation Detected! (r = {correlation:.2f})**
                                
                                Your productivity and mental wellness tend to move together. 
                                When one improves, the other often does too! Keep balancing both aspects.
                                """)
                            elif correlation < -0.3:
                                st.warning(f"""
                                **Negative Correlation Detected (r = {correlation:.2f})**
                                
                                There might be a trade-off between productivity and wellness.
                                Consider: Are you overworking? Remember to prioritize self-care!
                                """)
                            else:
                                st.info(f"""
                                **Weak Correlation (r = {correlation:.2f})**
                                
                                Your productivity and wellness appear independent.
                                Both are important - continue tracking to find your optimal balance!
                                """)
                    
                    # Best day analysis
                    if dates:
                        best_wellness_day = dates[np.argmax(avg_wellness)]
                        best_focus_day = dates[np.argmax(focus_mins)]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Best Wellness Day", 
                                     best_wellness_day.strftime("%B %d"),
                                     f"{max(avg_wellness):.0f}/100")
                        
                        with col2:
                            st.metric("Most Productive Day",
                                     best_focus_day.strftime("%B %d"),
                                     f"{max(focus_mins)} min")
            else:
                st.info("Use both Journal Analyzer and Focus Timer to see correlation insights!")
        
        # ====================================================================
        # CAMERA EMOTION ANALYSIS SECTION - MUST BE INSIDE THE ELSE BLOCK
        # ====================================================================
        st.markdown("---")
        st.subheader("📷 Camera-Based Emotion Analysis")

        # Get total image emotions FIRST
        total_image_emotions = len(st.session_state.get('image_emotions', []))

        # Show detailed debug info
        with st.expander("🔧 Debug Information", expanded=False):
            st.write(f"**Total emotions in memory:** {total_image_emotions}")
    
            if total_image_emotions > 0:
                st.write("**Sample emotion (first one):**")
                first_emotion = st.session_state.image_emotions[0]
                st.json({
                    'emotion': first_emotion.get('emotion'),
                    'confidence': first_emotion.get('confidence'),
                    'session_id': first_emotion.get('session_id', 'N/A'),
                    'timestamp': str(first_emotion.get('timestamp'))
                })
        
                # Show unique session IDs
                unique_sids = set(e.get('session_id', 'N/A') for e in st.session_state.image_emotions)
                st.write(f"**Unique session IDs in emotions:** {len(unique_sids)}")
                for sid in list(unique_sids):
                    st.text(sid[:80])
    
            # Check focus sessions
            if 'focus_sessions' in st.session_state:
                completed = [s for s in st.session_state.focus_sessions if s.get('completed')]
                st.write(f"**Completed focus sessions:** {len(completed)}")
        
                if completed:
                    st.write("**Session IDs in completed sessions:**")
                    for i, session in enumerate(completed[:3]):
                        sid = session.get('session_id', 'NOT SET')
                        st.text(f"{i}: {sid[:80]}")
                    
        if total_image_emotions == 0:
            st.info("No camera emotion data yet. Start a focus session with camera monitoring to collect data!")
            
            # Show instructions
            with st.expander("ℹ How to Enable Camera Monitoring"):
                st.write("""
                **Steps to collect camera emotion data:**
                
                1. Go to the **⏱ Focus Timer** page
                2. Check the box **"📷 Enable emotion monitoring via camera"**
                3. Start a focus session
                4. Your camera will capture your emotions every 5 seconds
                5. Return here after the session to see the analysis!
                
                **Note:** 
                - Camera images are analyzed and immediately deleted
                - Only emotion predictions are stored
                - You need to position your face in front of the camera
                """)
        else:
            # Show data is available
            st.success(f"✅ Found {total_image_emotions} emotion captures!")
            
            # Overall summary
            overall_summary = get_image_emotion_summary()
            
            if overall_summary:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Captures", overall_summary['total_captures'])
                
                with col2:
                    st.metric("Dominant Emotion", 
                             overall_summary['dominant_emotion'].title())
                
                with col3:
                    high_risk = overall_summary['risk_distribution']['high']
                    st.metric("High Risk Detections", high_risk)
                
                with col4:
                    low_risk = overall_summary['risk_distribution']['low']
                    st.metric("Positive Detections", low_risk)
                
                st.markdown("---")
                
                # Emotion distribution pie chart
                st.subheader("🎭 Overall Emotion Distribution")
                
                emotion_counts = overall_summary['emotion_counts']
                
                fig_pie = px.pie(
                    values=list(emotion_counts.values()),
                    names=list(emotion_counts.keys()),
                    title='Emotion Distribution Across All Sessions',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
                st.markdown("---")
                
                # Emotion timeline
                st.subheader("📈 Emotion Timeline")
                
                # Prepare data for timeline
                timeline_data = []
                for e in st.session_state.image_emotions:
                    timeline_data.append({
                        'Timestamp': e['timestamp'],
                        'Emotion': e['emotion'].title(),
                        'Confidence': e['confidence'],
                        'Session': e['session_id'][:15] + '...'
                    })
                
                if timeline_data:
                    df_timeline = pd.DataFrame(timeline_data)
                    
                    # Create interactive scatter plot
                    fig_timeline = px.scatter(
                        df_timeline,
                        x='Timestamp',
                        y='Emotion',
                        size='Confidence',
                        color='Emotion',
                        title='Emotion Timeline - All Captures',
                        hover_data=['Confidence', 'Session'],
                        size_max=15
                    )
                    fig_timeline.update_layout(height=400)
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    # Confidence distribution
                    st.subheader("📊 Confidence Scores Distribution")
                    
                    fig_conf = px.histogram(
                        df_timeline,
                        x='Confidence',
                        nbins=20,
                        title='Distribution of Prediction Confidence',
                        labels={'Confidence': 'Confidence Score', 'count': 'Number of Captures'}
                    )
                    fig_conf.update_layout(height=300)
                    st.plotly_chart(fig_conf, use_container_width=True)
                
                st.markdown("---")
                
                # Session-by-session analysis
                st.subheader("📊 Session-wise Emotion Analysis")
                
                sessions_with_data = get_all_sessions_with_image_data()
                
                if sessions_with_data:
                    st.write(f"**Found {len(sessions_with_data)} sessions with camera data**")
                    
                    # Show most recent sessions first
                    for session_data in reversed(sessions_with_data[-10:]):  # Show last 10
                        session = session_data['session']
                        summary = session_data['summary']
                        
                        # Format session date
                        session_date_str = session['date'].strftime('%Y-%m-%d %H:%M') if isinstance(session['date'], datetime) else str(session['date'])
                        
                        with st.expander(
                            f"📅 {session_date_str} | "
                            f"{session.get('notes', 'Focus Session')} | "
                            f"📷 {session_data['image_count']} captures",
                            expanded=False
                        ):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Emotion Breakdown:**")
                                for emotion, count in sorted(summary['emotion_counts'].items(), 
                                                            key=lambda x: x[1], 
                                                            reverse=True):
                                    percentage = (count / summary['total_captures']) * 100
                                    st.progress(percentage / 100, 
                                              text=f"{emotion.title()}: {count} ({percentage:.1f}%)")
                            
                            with col2:
                                st.write("**Risk Assessment:**")
                                risk_dist = summary['risk_distribution']
                                total_risk = sum(risk_dist.values())
                                
                                if total_risk > 0:
                                    st.write(f"🔴 High Risk: {risk_dist['high']} ({risk_dist['high']/total_risk*100:.1f}%)")
                                    st.write(f"🟡 Medium Risk: {risk_dist['medium']} ({risk_dist['medium']/total_risk*100:.1f}%)")
                                    st.write(f"🟢 Low Risk: {risk_dist['low']} ({risk_dist['low']/total_risk*100:.1f}%)")
                                
                                st.markdown("---")
                                st.write(f"**Dominant Emotion:** {summary['dominant_emotion'].title()}")
                                st.write(f"**Duration:** {session['duration']//60} minutes")
                    
                    st.markdown("---")
                    
                    # Emotion trends over sessions
                    st.subheader("📈 Emotion Trends Across Sessions")
                    
                    session_trend_data = []
                    for session_data in sessions_with_data:
                        session = session_data['session']
                        summary = session_data['summary']
                        
                        session_trend_data.append({
                            'Session Time': session['date'],
                            'Dominant Emotion': summary['dominant_emotion'].title(),
                            'Total Captures': summary['total_captures'],
                            'High Risk %': (summary['risk_distribution']['high'] / 
                                          summary['total_captures'] * 100) if summary['total_captures'] > 0 else 0,
                            'Positive %': (summary['risk_distribution']['low'] / 
                                         summary['total_captures'] * 100) if summary['total_captures'] > 0 else 0
                        })
                    
                    if session_trend_data:
                        df_trends = pd.DataFrame(session_trend_data)
                        
                        # High risk percentage trend
                        fig_risk = px.line(
                            df_trends,
                            x='Session Time',
                            y='High Risk %',
                            title='High Risk Emotion Percentage Over Sessions',
                            markers=True,
                            labels={'High Risk %': 'High Risk Emotions (%)'}
                        )
                        fig_risk.update_layout(height=300)
                        st.plotly_chart(fig_risk, use_container_width=True)
                        
                        # Positive percentage trend
                        fig_positive = px.line(
                            df_trends,
                            x='Session Time',
                            y='Positive %',
                            title='Positive Emotion Percentage Over Sessions',
                            markers=True,
                            line_shape='spline',
                            labels={'Positive %': 'Positive Emotions (%)'}
                        )
                        fig_positive.update_traces(line_color='green')
                        fig_positive.update_layout(height=300)
                        st.plotly_chart(fig_positive, use_container_width=True)
                        
                        # Bar chart of dominant emotions per session
                        st.subheader("🎭 Dominant Emotion by Session")
                        fig_dominant = px.bar(
                            df_trends,
                            x='Session Time',
                            y='Total Captures',
                            color='Dominant Emotion',
                            title='Session Emotions and Capture Count',
                            labels={'Total Captures': 'Number of Captures'}
                        )
                        fig_dominant.update_layout(height=300)
                        st.plotly_chart(fig_dominant, use_container_width=True)
                else:
                    st.warning("⚠ Camera data exists but no completed sessions with camera monitoring found.")
                    st.info("💡 Complete a focus session with camera enabled to see session-wise analysis.")
            else:
                st.error("❌ Error processing camera emotion data. Summary generation failed.")
                
                # Debug information
                with st.expander("🔧 Debug Information"):
                    st.write("**Raw Data Sample (first 3 entries):**")
                    for i, emotion in enumerate(st.session_state.image_emotions[:3]):
                        st.json({
                            'index': i,
                            'emotion': emotion.get('emotion'),
                            'confidence': emotion.get('confidence'),
                            'session_id': emotion.get('session_id', 'N/A')[:30] + '...',
                            'timestamp': str(emotion.get('timestamp'))
                        })
        
        st.markdown("---")
        st.subheader("💬 Perry Chat Emotional Trend Analysis")
        
        # Import the function
        from config import get_sentiment_trend_data
        
        sentiment_df = get_sentiment_trend_data()
        
        if sentiment_df is not None and len(sentiment_df) > 0:
            st.success(f"✅ Analyzed {len(sentiment_df)} conversations with Perry")
            
            # Stats row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_messages = len(sentiment_df)
                st.metric("Total Messages", total_messages)
            
            with col2:
                positive_count = len(sentiment_df[sentiment_df['sentiment'] == 'POSITIVE'])
                st.metric("😊 Positive", positive_count)
            
            with col3:
                neutral_count = len(sentiment_df[sentiment_df['sentiment'] == 'NEUTRAL'])
                st.metric("😐 Neutral", neutral_count)
            
            with col4:
                negative_count = len(sentiment_df[sentiment_df['sentiment'] == 'NEGATIVE'])
                st.metric("😔 Negative", negative_count)
            
            st.markdown("---")
            
            # Emotional Trend Over Time - LINE CHART
            st.subheader("📈 Your Emotional Journey with Perry")
            
            fig_trend = go.Figure()
            
            # Add line trace
            fig_trend.add_trace(go.Scatter(
                x=sentiment_df['timestamp'],
                y=sentiment_df['adjusted_score'],
                mode='lines+markers',
                name='Emotional Trend',
                line=dict(width=3),
                marker=dict(
                    size=10,
                    color=sentiment_df['adjusted_score'],
                    colorscale=[
                        [0, 'rgb(239, 68, 68)'],      # Red for negative
                        [0.5, 'rgb(234, 179, 8)'],     # Yellow for neutral
                        [1, 'rgb(34, 197, 94)']        # Green for positive
                    ],
                    showscale=True,
                    colorbar=dict(
                        title="Sentiment",
                        ticktext=["Negative", "Neutral", "Positive"],
                        tickvals=[-1, 0, 1]
                    )
                ),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.1)',
                hovertemplate='<b>%{x}</b><br>Sentiment Score: %{y:.2f}<extra></extra>'
            ))
            
            fig_trend.update_layout(
                title="Emotional Trend Over Time",
                xaxis_title="Date & Time",
                yaxis_title="Sentiment Score (-1 to +1)",
                height=400,
                yaxis=dict(range=[-1.2, 1.2]),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Last 7 Days Average
            st.markdown("---")
            st.subheader("📊 Last 7 Days Summary")
            
            # Filter last 7 days
            last_7_days = sentiment_df[
                sentiment_df['timestamp'] >= (datetime.now() - timedelta(days=7))
            ]
            
            if len(last_7_days) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_sentiment = last_7_days['adjusted_score'].mean()
                    mood_emoji = "😊" if avg_sentiment > 0.3 else "😐" if avg_sentiment > -0.3 else "😔"
                    st.metric("Average Mood", f"{mood_emoji} {avg_sentiment:.2f}")
                
                with col2:
                    message_count = len(last_7_days)
                    st.metric("Messages (7d)", message_count)
                
                with col3:
                    positive_ratio = len(last_7_days[last_7_days['sentiment'] == 'POSITIVE']) / len(last_7_days) * 100
                    st.metric("Positivity Rate", f"{positive_ratio:.0f}%")
                
                # Daily breakdown bar chart
                st.markdown("---")
                st.write("**Daily Sentiment Breakdown:**")
                
                # Group by date
                last_7_days['date'] = last_7_days['timestamp'].dt.date
                daily_sentiment = last_7_days.groupby('date')['adjusted_score'].mean().reset_index()
                
                fig_daily = go.Figure()
                
                fig_daily.add_trace(go.Bar(
                    x=daily_sentiment['date'],
                    y=daily_sentiment['adjusted_score'],
                    marker_color=[
                        'rgb(34, 197, 94)' if score > 0.3 else 
                        'rgb(234, 179, 8)' if score > -0.3 else 
                        'rgb(239, 68, 68)'
                        for score in daily_sentiment['adjusted_score']
                    ],
                    text=[f"{score:.2f}" for score in daily_sentiment['adjusted_score']],
                    textposition='auto'
                ))
                
                fig_daily.update_layout(
                    title="Average Daily Sentiment",
                    xaxis_title="Date",
                    yaxis_title="Avg Sentiment Score",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig_daily, use_container_width=True)
                
                # Insights
                st.markdown("---")
                st.subheader("💡 Insights")
                
                if avg_sentiment > 0.3:
                    st.success("""
                    **Great emotional trend! 🎉**
                    
                    Your recent conversations show predominantly positive emotions. You're doing well!
                    - Keep up the good work with self-reflection
                    - Continue sharing positive experiences with Perry
                    """)
                elif avg_sentiment > -0.3:
                    st.info("""
                    **Balanced emotional state 😊**
                    
                    Your emotions show a healthy mix. This is normal!
                    - Continue regular check-ins with Perry
                    - Notice patterns in your daily mood
                    """)
                else:
                    st.warning("""
                    **We notice some challenges 💙**
                    
                    Your recent conversations show some difficulty. Remember:
                    - It's okay to not be okay
                    - Keep talking to Perry - expression helps
                    - Consider reaching out to a professional if needed
                    """)
            else:
                st.info("Start chatting with Perry in the last 7 days to see your emotional trend!")
            
            # Sentiment Distribution Pie Chart
            st.markdown("---")
            st.subheader("🎭 Overall Sentiment Distribution")
            
            sentiment_counts = sentiment_df['sentiment'].value_counts()
            
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title='Distribution of Sentiments',
                color=sentiment_counts.index,
                color_discrete_map={
                    'POSITIVE': '#22c55e',
                    'NEUTRAL': '#eab308',
                    'NEGATIVE': '#ef4444'
                }
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
        else:
            st.info("💬 Start talking to Perry to see your emotional trend analysis!")
            st.write("**Why track your emotional trend?**")
            st.write("- 📊 Identify patterns in your mental health")
            st.write("- 🎯 Understand what affects your mood")
            st.write("- 💪 Celebrate improvements and progress")
            st.write("- 🧠 Gain self-awareness through data")
            if st.button("💬 Start Chatting with Perry Now"):
                st.session_state.current_page = "💬 Talk to Perry"
                st.rerun()

# ============================================================================
# PAGE 6: PRODUCTIVITY REPORT
# ============================================================================
def show_productivity_report():
    st.markdown('<h1 class="main-header">📈 Comprehensive Productivity Report</h1>', unsafe_allow_html=True)
    
    if not st.session_state.focus_sessions:
        st.info("Start completing focus sessions to generate your productivity report!")
    else:
        completed = [s for s in st.session_state.focus_sessions if s['completed']]
        
        if not completed:
            st.info("Complete at least one focus session to see your report!")
        else:
            # Report date range
            start_date = min(s['date'] for s in completed).date()
            end_date = max(s['date'] for s in completed).date()
            days_tracked = (end_date - start_date).days + 1
            
            st.info(f"📅 Report Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')} ({days_tracked} days)")
            
            # Summary metrics
            st.subheader("📊 Summary Statistics")
            
            total_minutes = sum(s['duration'] for s in completed) // 60
            total_hours = total_minutes / 60
            total_sessions = len(completed)
            avg_session = total_minutes // total_sessions if total_sessions > 0 else 0
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Focus Time", f"{total_hours:.1f} hrs")
            
            with col2:
                st.metric("Total Sessions", total_sessions)
            
            with col3:
                st.metric("Avg Session", f"{avg_session} min")
            
            with col4:
                streak = calculate_study_streak()
                st.metric("Current Streak", f"{streak} 🔥")
            
            with col5:
                avg_daily = total_minutes // days_tracked if days_tracked > 0 else 0
                st.metric("Avg Daily", f"{avg_daily} min")
            
            st.markdown("---")
            
            # Detailed breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 Weekly Breakdown")
                
                # Group by week
                weekly_data = defaultdict(int)
                for session in completed:
                    week_start = session['date'].date() - timedelta(days=session['date'].weekday())
                    weekly_data[week_start] += session['duration'] // 60
                
                weeks = sorted(weekly_data.keys())
                week_minutes = [weekly_data[w] for w in weeks]
                week_labels = [f"Week of {w.strftime('%b %d')}" for w in weeks]
                
                fig_weekly = go.Figure()
                fig_weekly.add_trace(go.Bar(
                    x=week_labels,
                    y=week_minutes,
                    marker_color='#667eea',
                    text=week_minutes,
                    textposition='auto'
                ))
                fig_weekly.update_layout(
                    xaxis_title="Week",
                    yaxis_title="Minutes",
                    height=300
                )
                st.plotly_chart(fig_weekly, use_container_width=True)
            
            with col2:
                st.subheader("⏱️ Session Length Analysis")
                
                duration_bins = {
                    '< 15 min': 0,
                    '15-30 min': 0,
                    '30-45 min': 0,
                    '45-60 min': 0,
                    '> 60 min': 0
                }
                
                for session in completed:
                    mins = session['duration'] // 60
                    if mins < 15:
                        duration_bins['< 15 min'] += 1
                    elif mins < 30:
                        duration_bins['15-30 min'] += 1
                    elif mins < 45:
                        duration_bins['30-45 min'] += 1
                    elif mins < 60:
                        duration_bins['45-60 min'] += 1
                    else:
                        duration_bins['> 60 min'] += 1
                
                fig_bins = px.pie(
                    values=list(duration_bins.values()),
                    names=list(duration_bins.keys()),
                    title="Session Duration Distribution"
                )
                st.plotly_chart(fig_bins, use_container_width=True)
            
            # Achievements & Milestones
            st.markdown("---")
            st.subheader("🎯 Achievements & Milestones")
            
            achievements = []
            
            if total_hours >= 10:
                achievements.append("🏆 10+ Hours of Focus Time")
            if total_sessions >= 20:
                achievements.append("📚 20+ Focus Sessions")
            if streak >= 7:
                achievements.append("🔥 Week-Long Streak")
            if streak >= 30:
                achievements.append("💎 Month-Long Streak")
            if any(s['duration'] >= 3600 for s in completed):
                achievements.append("⏱️ Marathon Session (60+ min)")
            
            if achievements:
                cols = st.columns(min(3, len(achievements)))
                for i, achievement in enumerate(achievements):
                    with cols[i % 3]:
                        st.success(achievement)
            else:
                st.info("Keep going to unlock achievements!")
            
            # Goals & recommendations
            st.markdown("---")
            st.subheader("🎯 Goals & Recommendations")
            
            # Weekly goal (5 hours)
            weekly_goal = 300
            this_week_mins = sum(
                s['duration'] // 60 for s in completed 
                if s['date'].date() >= (datetime.now().date() - timedelta(days=datetime.now().weekday()))
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Weekly Goal Progress**")
                progress = min(100, (this_week_mins / weekly_goal) * 100)
                st.progress(progress / 100)
                st.caption(f"{this_week_mins} / {weekly_goal} minutes ({progress:.0f}%)")
            
            with col2:
                st.markdown("**Recommendations**")
                if avg_session < 25:
                    st.write("💡 Try longer sessions (25+ min) for deeper focus")
                if streak == 0:
                    st.write("🔥 Start a new streak today!")
                if avg_daily < 30:
                    st.write("📈 Aim for 30+ minutes daily for consistency")
                else:
                    st.write("🎉 Great consistency! Keep it up!")
            
            # Export data
            st.markdown("---")
            st.subheader("📥 Export Your Data")
            
            if st.button("📄 Generate CSV Report"):
                df_sessions = pd.DataFrame([{
                    'Date': s['date'].strftime('%Y-%m-%d'),
                    'Time': s['date'].strftime('%H:%M'),
                    'Duration (minutes)': s['duration'] // 60,
                    'Notes': s.get('notes', '')
                } for s in completed])
                
                csv = df_sessions.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download Productivity Report",
                    data=csv,
                    file_name=f"productivity_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )