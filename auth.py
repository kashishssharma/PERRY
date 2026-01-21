# auth.py
# Perry Authentication System with Gen-Z UI
# UPDATED VERSION WITH LAST LOGIN FIX

import streamlit as st
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
import time as time_module

# ============================================================================
# USER DATABASE MANAGEMENT
# ============================================================================

def get_users_db_path():
    """Get path to users database file"""
    return Path("perry_users.json")

def load_users():
    """Load users from JSON database"""
    db_path = get_users_db_path()
    if db_path.exists():
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON database"""
    db_path = get_users_db_path()
    with open(db_path, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

# ============================================================================
# GEN-Z THEMED CSS
# ============================================================================

def get_auth_css():
    """Return Gen-Z themed CSS for authentication pages"""
    return """
    <style>
        /* Import Gen-Z Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
        
        /* Global Styles */
        .auth-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 30px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin: 2rem auto;
            max-width: 500px;
            animation: slideUp 0.5s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .auth-header {
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }
        
        .auth-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 20px rgba(0,0,0,0.2);
        }
        
        .auth-subtitle {
            font-family: 'Poppins', sans-serif;
            font-size: 1.1rem;
            color: rgba(255,255,255,0.9);
            font-weight: 300;
        }
        
        .auth-emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        /* Input Styling */
        .stTextInput input, .stSelectbox select, .stDateInput input {
            border: 2px solid transparent !important;
            border-radius: 15px !important;
            padding: 15px !important;
            background: transparent !important;
            font-family: 'Poppins', sans-serif !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: #764ba2 !important;
            background: transparent !important;
            box-shadow: 0 0 20px rgba(118,75,162,0.3) !important;
            transform: scale(1.02);
        }
        
        /* Button Styling */
        .stButton button {
            background: linear-gradient(45deg, #FF6B9D, #FFA06B) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 15px 40px !important;
            font-family: 'Poppins', sans-serif !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 10px 30px rgba(255,107,157,0.4) !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            width: 100% !important;
        }
        
        .stButton button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(255,107,157,0.6) !important;
        }
        
        .stButton button:active {
            transform: translateY(-1px) !important;
        }
        
        /* Toggle Switch */
        .auth-toggle {
            text-align: center;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .auth-toggle-text {
            color: white;
            font-family: 'Poppins', sans-serif;
            margin-bottom: 1rem;
        }
        
        .auth-toggle-btn {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            color: white;
            padding: 10px 30px;
            border-radius: 25px;
            border: 2px solid rgba(255,255,255,0.3);
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .auth-toggle-btn:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
            transform: scale(1.05);
        }
        
        /* Success/Error Messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 15px !important;
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* Form Labels */
        .stTextInput label, .stSelectbox label, .stDateInput label {
            color: white !important;
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        /* Columns in Forms */
        .row-widget.stHorizontal {
            gap: 1rem;
        }
        
        /* Loading Animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 1.5s infinite;
        }
    </style>
    """

# ============================================================================
# LOGIN PAGE
# ============================================================================

def show_login_page():
    """Display login page with Gen-Z styling"""
    
    st.markdown(get_auth_css(), unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown('''
            <div class="auth-header">
                <div class="auth-emoji">🎯</div>
                <div class="auth-title">PERRY</div>
                <div class="auth-subtitle">Your Mental Health & Productivity Buddy</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("🚀 LOGIN")
            
            if submit:
                if not email or not password:
                    st.error("⚠️ Please fill in all fields!")
                else:
                    users = load_users()
                    
                    if email in users:
                        if users[email]['password'] == hash_password(password):
                            # ✅ UPDATE LAST LOGIN TIME BEFORE SETTING SESSION
                            users[email]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            save_users(users)
                            
                            # Successful login with updated user data
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.session_state.user_data = users[email]  # This now includes updated last_login
                            st.success(f"✅ Welcome back, {users[email]['name']}! 🎉")
                            time_module.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Incorrect password!")
                    else:
                        st.error("❌ Email not registered. Please sign up!")
        
        # Toggle to Sign Up
        st.markdown('''
            <div class="auth-toggle">
                <p class="auth-toggle-text">Don't have an account?</p>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("✨ CREATE NEW ACCOUNT", key="toggle_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SIGNUP PAGE
# ============================================================================

def show_signup_page():
    """Display signup page with Gen-Z styling"""
    
    st.markdown(get_auth_css(), unsafe_allow_html=True)
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown('''
            <div class="auth-header">
                <div class="auth-emoji">✨</div>
                <div class="auth-title">JOIN PERRY</div>
                <div class="auth-subtitle">Start Your Journey to Better You</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Signup Form
        with st.form("signup_form", clear_on_submit=False):
            # Basic Info
            name = st.text_input("👤 Full Name", placeholder="John Doe")
            
            col_a, col_b = st.columns(2)
            with col_a:
                email = st.text_input("📧 Email", placeholder="john@example.com")
            with col_b:
                phone = st.text_input("📱 Phone", placeholder="9876543210")
            
            col_c, col_d = st.columns(2)
            with col_c:
                gender = st.selectbox("⚧️ Gender", ["", "Male", "Female", "Non-Binary", "Prefer not to say"])
            with col_d:
                dob = st.date_input("🎂 Date of Birth", 
                                   min_value=datetime(1950, 1, 1),
                                   max_value=datetime.now(),
                                   value=datetime(2000, 1, 1))
            
            # Goals
            goal = st.selectbox("🎯 Primary Goal", [
                "",
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
            ])
            
            other_goal = None
            if goal == "✨ Other":
                other_goal = st.text_input("Specify your goal:", placeholder="e.g., Content Creation")
            
            # Password
            password = st.text_input("🔒 Create Password", type="password", 
                                    placeholder="Min. 8 chars, 1 uppercase, 1 number")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", 
                                            placeholder="Re-enter your password")
            
            submit = st.form_submit_button("🎉 CREATE ACCOUNT")
            
            if submit:
                # Validation
                errors = []
                
                if not name or not email or not phone or not gender or not goal or not password or not confirm_password:
                    errors.append("⚠️ Please fill in all required fields!")
                
                if email and not validate_email(email):
                    errors.append("❌ Invalid email format!")
                
                if phone and not validate_phone(phone):
                    errors.append("❌ Invalid phone number! Must be 10 digits starting with 6-9")
                
                if password:
                    is_valid, msg = validate_password(password)
                    if not is_valid:
                        errors.append(f"❌ {msg}")
                
                if password != confirm_password:
                    errors.append("❌ Passwords don't match!")
                
                # Check if email already exists
                users = load_users()
                if email in users:
                    errors.append("❌ Email already registered! Please login.")
                
                # Show errors
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create new user
                    final_goal = other_goal if goal == "✨ Other" and other_goal else goal
                    
                    new_user = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'gender': gender,
                        'dob': dob.strftime('%Y-%m-%d'),
                        'goal': final_goal,
                        'password': hash_password(password),
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'last_login': None  # Will be set on first login
                    }
                    
                    users[email] = new_user
                    save_users(users)
                    
                    st.success(f"🎉 Welcome aboard, {name}! Your account has been created!")
                    st.info("✅ Redirecting to login...")
                    time_module.sleep(2)
                    st.session_state.auth_page = "login"
                    st.rerun()
        
        # Toggle to Login
        st.markdown('''
            <div class="auth-toggle">
                <p class="auth-toggle-text">Already have an account?</p>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🔑 LOGIN INSTEAD", key="toggle_login"):
            st.session_state.auth_page = "login"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MAIN AUTHENTICATION FUNCTION
# ============================================================================

def show_auth_page():
    """Main authentication handler"""
    
    # Hide Streamlit default elements
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
    
    # Show appropriate page
    if st.session_state.auth_page == "login":
        show_login_page()
    else:
        show_signup_page()

# ============================================================================
# LOGOUT FUNCTION
# ============================================================================

def logout_user():
    """Logout current user"""
    if 'user_email' in st.session_state:
        # Update last login time on logout as well
        users = load_users()
        if st.session_state.user_email in users:
            users[st.session_state.user_email]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_users(users)
    
    # Clear session
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_data = None
    st.rerun()

# ============================================================================
# USER PROFILE DISPLAY (ENHANCED VERSION)
# ============================================================================

def show_user_profile_sidebar():
    """Display user profile in sidebar with navigation to full profile"""
    if st.session_state.get('authenticated', False):
        user_data = st.session_state.get('user_data', {})
        
        # Get avatar emoji based on first letter of name
        def get_avatar(name):
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
        
        avatar = get_avatar(user_data.get('name', 'User'))
        name = user_data.get('name', 'User')
        goal = user_data.get('goal', 'No goal set')
        
        st.sidebar.markdown("---")
        
        # Beautiful profile card in sidebar
        st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{avatar}</div>
            <div style="color: white; font-weight: 700; font-size: 1.2rem; margin-bottom: 0.3rem;">
                {name}
            </div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-bottom: 1rem;">
                {goal}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile and logout buttons
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("👤 Profile", use_container_width=True):
                st.session_state.navigate_to = "👤 My Profile"
                st.rerun()
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()