# profile_page.py
# Perry User Profile Page with Beautiful UI
# Save this as profile_page.py in the same folder as app2.py

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from auth import load_users, save_users, validate_phone

# ============================================================================
# PROFILE PAGE CSS
# ============================================================================

def get_profile_css():
    """Return beautiful CSS for profile page"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
        
        .profile-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            padding: 2.5rem;
            margin: 1rem 0;
            box-shadow: 0 15px 50px rgba(0,0,0,0.2);
            animation: fadeIn 0.6s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .profile-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .profile-avatar {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF6B9D, #FFA06B);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.5rem;
            margin: 0 auto 1rem;
            box-shadow: 0 10px 30px rgba(255,107,157,0.4);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }
        
        .profile-name {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        
        .profile-email {
            font-family: 'Poppins', sans-serif;
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        
        .profile-joined {
            font-family: 'Poppins', sans-serif;
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
        }
        
        .info-card {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .info-label {
            font-family: 'Poppins', sans-serif;
            color: rgba(255,255,255,0.8);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .info-value {
            font-family: 'Space Grotesk', sans-serif;
            color: white;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .goal-card {
            background: linear-gradient(135deg, #FF6B9D, #FFA06B);
            border-radius: 20px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 10px 40px rgba(255,107,157,0.3);
            text-align: center;
        }
        
        .goal-emoji {
            font-size: 3rem;
            margin-bottom: 1rem;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .goal-text {
            font-family: 'Space Grotesk', sans-serif;
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        
        .edit-mode-banner {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            color: white;
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            margin-bottom: 1.5rem;
            animation: slideDown 0.4s ease-out;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            background: rgba(255,255,255,0.15);
            transform: scale(1.05);
        }
        
        .stat-emoji {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-family: 'Poppins', sans-serif;
            color: rgba(255,255,255,0.8);
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
        }
        
        .stat-value {
            font-family: 'Space Grotesk', sans-serif;
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        /* Button Overrides for Profile Page */
        .profile-container .stButton button {
            background: linear-gradient(45deg, #FF6B9D, #FFA06B) !important;
            color: white !important;
            border: none !important;
            border-radius: 15px !important;
            padding: 12px 30px !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .profile-container .stButton button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 30px rgba(255,107,157,0.4) !important;
        }
        
        /* Selectbox Styling */
        .profile-container .stSelectbox select {
            background: rgba(255,255,255,0.2) !important;
            color: white !important;
            border: 2px solid rgba(255,255,255,0.3) !important;
            border-radius: 15px !important;
            padding: 12px !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
        }
        
        .profile-container .stSelectbox label {
            color: white !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
        }
    </style>
    """

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_avatar(name):
    """Get emoji avatar based on first letter of name"""
    avatars = {
        'A': '🌟', 'B': '🎨', 'C': '🎯', 'D': '💎', 'E': '🌈',
        'F': '🔥', 'G': '🌺', 'H': '🎭', 'I': '✨', 'J': '🎪',
        'K': '🦋', 'L': '🌙', 'M': '🎵', 'N': '🌸', 'O': '🎨',
        'P': '🎪', 'Q': '👑', 'R': '🚀', 'S': '⭐', 'T': '🎯',
        'U': '🦄', 'V': '🎻', 'W': '🌊', 'X': '❌', 'Y': '🌟',
        'Z': '⚡'
    }
    first_letter = name[0].upper() if name else 'P'
    return avatars.get(first_letter, '👤')

def calculate_days_since_joining(created_at):
    """Calculate days since account creation"""
    try:
        created_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        days = (datetime.now() - created_date).days
        return days
    except:
        return 0

def get_goal_emoji(goal):
    """Get emoji for goal"""
    goal_emojis = {
        '📚 Study & Academic Excellence': '📚',
        '💼 Work Productivity': '💼',
        '🎨 Creative Projects': '🎨',
        '💪 Fitness & Health': '💪',
        '🧘 Mental Wellness': '🧘',
        '📊 Business & Entrepreneurship': '📊',
        '🎮 Gaming & Esports': '🎮',
        '🎵 Music & Arts': '🎵',
        '📖 Learning New Skills': '📖',
    }
    return goal_emojis.get(goal, '🎯')

# ============================================================================
# MAIN PROFILE PAGE
# ============================================================================

def show_profile_page():
    """Display user profile page"""
    
    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        st.error("❌ Please login to view your profile")
        return
    
    # Load user data
    user_email = st.session_state.get('user_email')
    users = load_users()
    
    if user_email not in users:
        st.error("❌ User data not found")
        return
    
    user_data = users[user_email]
    
    # Apply CSS
    st.markdown(get_profile_css(), unsafe_allow_html=True)
    
    # Initialize edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    # Edit Mode Banner
    if st.session_state.edit_mode:
        st.markdown('''
            <div class="edit-mode-banner">
                ✏️ EDIT MODE ACTIVE - Update your goal below
            </div>
        ''', unsafe_allow_html=True)
    
    # Profile Container
    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    
    # ========== PROFILE HEADER ==========
    avatar_emoji = get_user_avatar(user_data.get('name', 'User'))
    
    st.markdown(f'''
        <div class="profile-header">
            <div class="profile-avatar">{avatar_emoji}</div>
            <div class="profile-name">{user_data.get('name', 'User')}</div>
            <div class="profile-email">📧 {user_data.get('email', 'N/A')}</div>
            <div class="profile-joined">
                🎉 Joined {calculate_days_since_joining(user_data.get('created_at', ''))} days ago
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== BASIC INFO CARDS ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
            <div class="info-card">
                <div class="info-label">📱 Phone Number</div>
                <div class="info-value">{user_data.get('phone', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'''
            <div class="info-card">
                <div class="info-label">🎂 Date of Birth</div>
                <div class="info-value">{user_data.get('dob', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="info-card">
                <div class="info-label">⚧️ Gender</div>
                <div class="info-value">{user_data.get('gender', 'N/A')}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        last_login = user_data.get('last_login', 'Never')
        if last_login and last_login != 'Never':
            try:
                login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
                last_login = login_date.strftime('%b %d, %Y at %I:%M %p')
            except:
                pass
        
        st.markdown(f'''
            <div class="info-card">
                <div class="info-label">🕐 Last Login</div>
                <div class="info-value" style="font-size: 1rem;">{last_login}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== CURRENT GOAL DISPLAY ==========
    current_goal = user_data.get('goal', '🎯 No goal set')
    goal_emoji = get_goal_emoji(current_goal)
    
    if not st.session_state.edit_mode:
        st.markdown(f'''
            <div class="goal-card">
                <div class="goal-emoji">{goal_emoji}</div>
                <div class="info-label">CURRENT GOAL</div>
                <div class="goal-text">{current_goal}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Edit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✏️ EDIT GOAL", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
    
    # ========== GOAL EDITOR ==========
    else:
        st.markdown("### 🎯 Update Your Goal")
        
        goal_options = [
            "📚 Study & Academic Excellence",
            "💼 Work Productivity",
            "🎨 Creative Projects",
            "💪 Fitness & Health",
            "🧘 Mental Wellness",
            "📊 Business & Entrepreneurship",
            "🎮 Gaming & Esports",
            "🎵 Music & Arts",
            "📖 Learning New Skills",
            "✨ Other"
        ]
        
        # Find current index
        try:
            current_index = goal_options.index(current_goal)
        except:
            current_index = 0
        
        new_goal = st.selectbox(
            "Select your new goal:",
            goal_options,
            index=current_index,
            key="goal_selector"
        )
        
        other_goal = None
        if new_goal == "✨ Other":
            other_goal = st.text_input(
                "Specify your goal:",
                placeholder="e.g., Content Creation",
                key="other_goal_input"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 SAVE CHANGES", use_container_width=True):
                final_goal = other_goal if new_goal == "✨ Other" and other_goal else new_goal
                
                if not final_goal or (new_goal == "✨ Other" and not other_goal):
                    st.error("❌ Please specify your goal!")
                else:
                    # Update user data
                    users[user_email]['goal'] = final_goal
                    save_users(users)
                    
                    # Update session state
                    st.session_state.user_data['goal'] = final_goal
                    st.session_state.edit_mode = False
                    
                    st.success(f"✅ Goal updated to: {final_goal}")
                    st.balloons()
                    st.rerun()
        
        with col2:
            if st.button("❌ CANCEL", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()
    
    # ========== ACCOUNT STATS ==========
    st.markdown("---")
    st.markdown("### 📊 Account Statistics")
    
    days_active = calculate_days_since_joining(user_data.get('created_at', ''))
    total_sessions = len(st.session_state.get('focus_sessions', []))
    total_entries = len(st.session_state.get('emotion_history', []))
    total_schedules = len(st.session_state.get('schedules', []))
    
    st.markdown(f'''
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-emoji">📅</div>
                <div class="stat-label">Days Active</div>
                <div class="stat-value">{days_active}</div>
            </div>
            <div class="stat-card">
                <div class="stat-emoji">⏱️</div>
                <div class="stat-label">Focus Sessions</div>
                <div class="stat-value">{total_sessions}</div>
            </div>
            <div class="stat-card">
                <div class="stat-emoji">📝</div>
                <div class="stat-label">Journal Entries</div>
                <div class="stat-value">{total_entries}</div>
            </div>
            <div class="stat-card">
                <div class="stat-emoji">✅</div>
                <div class="stat-label">Total Tasks</div>
                <div class="stat-value">{total_schedules}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== ACCOUNT ACTIONS ==========
    st.markdown("---")
    
    with st.expander("⚙️ Account Settings", expanded=False):
        st.warning("⚠️ Danger Zone")
        
        st.markdown("**Account Information:**")
        st.info(f"""
        - **Account Created:** {user_data.get('created_at', 'N/A')}
        - **Email:** {user_data.get('email', 'N/A')}
        - **User ID:** {user_email}
        """)
        
        st.markdown("---")
        
        # Export data button
        if st.button("📥 Export My Data", use_container_width=True):
            import json
            export_data = {
                'user_info': user_data,
                'focus_sessions': st.session_state.get('focus_sessions', []),
                'emotion_history': st.session_state.get('emotion_history', []),
                'schedules': st.session_state.get('schedules', []),
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.download_button(
                label="⬇️ Download Data (JSON)",
                data=json.dumps(export_data, indent=4),
                file_name=f"perry_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            st.success("✅ Data ready for download!")

# ============================================================================
# QUICK PROFILE WIDGET (for sidebar or dashboard)
# ============================================================================

def show_profile_widget():
    """Show compact profile widget"""
    if not st.session_state.get('authenticated', False):
        return
    
    user_data = st.session_state.get('user_data', {})
    avatar = get_user_avatar(user_data.get('name', 'User'))
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f'''
            <div style="font-size: 3rem; text-align: center;">
                {avatar}
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**{user_data.get('name', 'User')}**")
        st.caption(f"{user_data.get('goal', 'No goal set')}")
    
    if st.button("👤 View Full Profile", use_container_width=True):
        st.session_state.navigate_to = "👤 My Profile"
        st.rerun()