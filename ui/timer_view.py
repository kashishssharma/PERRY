import streamlit as st
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def render_timer(timer_manager, stats_manager, task_manager, audio_manager):
    """Render the focus timer view"""
    st.markdown('<h1 class="main-header">⏱️ Focus Timer</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Timer display
        timer_info = timer_manager.get_session_info()
        
        # Phase display
        phase_emoji = "🎯" if timer_info['phase'] == 'focus' else "☕" if 'break' in timer_info['phase'] else "⏸️"
        phase_text = timer_info['phase'].replace('_', ' ').title()
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin-bottom: 2rem;">
            <h3 style="margin: 0;">Session #{timer_info['session_count']}</h3>
            <h1 style="font-size: 5rem; margin: 1rem 0; font-weight: bold;">{timer_info['formatted_time']}</h1>
            <p style="font-size: 1.5rem; margin: 0;">{phase_emoji} {phase_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = timer_info['progress'] / 100
        st.progress(progress)
        st.caption(f"Progress: {timer_info['progress']:.1f}%")
        
        # Controls
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if not timer_info['is_running']:
                if st.button("▶️ Start", use_container_width=True, type="primary"):
                    timer_manager.start_focus_session(st.session_state.focus_duration)
                    audio_manager.play_start_sound()
                    st.rerun()
            elif timer_info['is_paused']:
                if st.button("▶️ Resume", use_container_width=True, type="primary"):
                    timer_manager.resume()
                    st.rerun()
            else:
                if st.button("⏸️ Pause", use_container_width=True):
                    timer_manager.pause()
                    st.rerun()
        
        with col_b:
            if st.button("⏹️ Stop", use_container_width=True):
                if timer_info['is_running']:
                    elapsed = timer_manager.get_elapsed_time()
                    if elapsed > 60:
                        stats_manager.add_session_time(elapsed)
                        audio_manager.play_end_sound()
                timer_manager.stop()
                st.rerun()
        
        with col_c:
            if st.button("🔄 Reset", use_container_width=True):
                timer_manager.reset()
                st.rerun()
        
        # Session info
        st.markdown("---")
        st.subheader("📊 Session Statistics")
        
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.metric("Completed", f"{timer_info['completed_sessions']}")
        with col_y:
            next_break = "Long" if timer_info['session_count'] % config.SESSIONS_BEFORE_LONG_BREAK == 0 else "Short"
            st.metric("Next Break", next_break)
        with col_z:
            today_stats = stats_manager.get_today_stats()
            st.metric("Today", today_stats['study_time_formatted'])
        
        # Auto-refresh
        if timer_info['is_running'] and not timer_info['is_paused']:
            time.sleep(1)
            st.rerun()
    
    with col2:
        # Timer settings
        st.subheader("⚙️ Timer Settings")
        
        st.session_state.focus_duration = st.number_input(
            "Focus Time (min)",
            min_value=1,
            max_value=120,
            value=st.session_state.get('focus_duration', config.DEFAULT_FOCUS_TIME),
            step=5,
            help="Duration of focus sessions"
        )
        
        st.session_state.short_break_duration = st.number_input(
            "Short Break (min)",
            min_value=1,
            max_value=30,
            value=st.session_state.get('short_break_duration', config.DEFAULT_SHORT_BREAK),
            step=1,
            help="Duration of short breaks"
        )
        
        st.session_state.long_break_duration = st.number_input(
            "Long Break (min)",
            min_value=1,
            max_value=60,
            value=st.session_state.get('long_break_duration', config.DEFAULT_LONG_BREAK),
            step=5,
            help="Duration of long breaks"
        )
        
        st.markdown("---")
        
        # Task manager
        st.subheader("📝 Tasks")
        
        # Add task
        with st.form("add_task_form"):
            new_task = st.text_input("New task", placeholder="What do you need to do?")
            priority = st.selectbox("Priority", ["High", "Normal", "Low"])
            
            if st.form_submit_button("➕ Add Task", use_container_width=True):
                if new_task.strip():
                    task_manager.add_task(new_task, priority)
                    st.success("Task added!")
                    st.rerun()
        
        # Display tasks
        pending_tasks = task_manager.get_pending_tasks()
        
        if pending_tasks:
            for task in pending_tasks:
                col_task, col_btn = st.columns([3, 1])
                
                with col_task:
                    priority_emoji = "🔴" if task['priority'] == "High" else "🟡" if task['priority'] == "Normal" else "🟢"
                    if st.checkbox(
                        f"{priority_emoji} {task['text']}", 
                        key=f"task_{task['id']}",
                        value=task['completed']
                    ):
                        task_manager.complete_task(task['id'])
                        stats_manager.add_completed_task(task['text'])
                        st.success("✅ Task completed!")
                        st.rerun()
                
                with col_btn:
                    if st.button("🗑️", key=f"del_{task['id']}"):
                        task_manager.delete_task(task['id'])
                        st.rerun()
        else:
            st.info("No tasks yet!")