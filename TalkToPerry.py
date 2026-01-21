# -*- coding: utf-8 -*-
# TalkToPerry.py
# Mental Health Chatbot Page - Perry Your AI Companion

import streamlit as st
from datetime import datetime
from config import perry_chat, analyze_sentiment_for_perry
from activity_logger import ACTIVITY_TYPES, log_user_activity
import time

def show_talk_to_perry():
    """Display the Talk to Perry chatbot page"""
    
    # Apply dark mode styling
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .chat-container {
            background: #1a202c;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            max-height: 500px;
            overflow-y: auto;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 18px;
            border-radius: 18px 18px 4px 18px;
            margin: 10px 0 10px auto;
            max-width: 70%;
            float: right;
            clear: both;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }
        .perry-message {
            background: #2d3748;
            color: #e2e8f0;
            padding: 12px 18px;
            border-radius: 18px 18px 18px 4px;
            margin: 10px auto 10px 0;
            max-width: 70%;
            float: left;
            clear: both;
            border: 1px solid rgba(102, 126, 234, 0.3);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        .perry-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            float: left;
            margin-right: 10px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        }
        .message-wrapper {
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
            clear: both;
        }
        .input-container {
            position: sticky;
            bottom: 0;
            background: #1a202c;
            padding: 15px;
            border-top: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 0 0 15px 15px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .chat-container {
            background: #f5f7fa;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            max-height: 500px;
            overflow-y: auto;
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 18px;
            border-radius: 18px 18px 4px 18px;
            margin: 10px 0 10px auto;
            max-width: 70%;
            float: right;
            clear: both;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        .perry-message {
            background: white;
            color: #333;
            padding: 12px 18px;
            border-radius: 18px 18px 18px 4px;
            margin: 10px auto 10px 0;
            max-width: 70%;
            float: left;
            clear: both;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .perry-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            float: left;
            margin-right: 10px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        .message-wrapper {
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
            clear: both;
        }
        .input-container {
            position: sticky;
            bottom: 0;
            background: #f5f7fa;
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            border-radius: 0 0 15px 15px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">💬 Talk to Perry - Your Mental Health Companion</h1>', 
                unsafe_allow_html=True)
    
    st.info("👋 Hi! I'm Perry, your mental health companion. Share your thoughts, feelings, or just chat with me. I'm here to listen and support you!")
    
    # Initialize chat history in session state
    if 'perry_chat_history' not in st.session_state:
        st.session_state.perry_chat_history = [{
            'role': 'assistant',
            'content': "Hello! I'm Perry, your mental health companion. How are you feeling today? Feel free to share anything that's on your mind.",
            'timestamp': datetime.now()
        }]
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.perry_chat_history:
            if message['role'] == 'user':
                st.markdown(
                    f'<div class="user-message">{message["content"]}</div><div style="clear: both;"></div>',
                    unsafe_allow_html=True
                )
            else:  # assistant (Perry)
                st.markdown(
                    f'<div class="message-wrapper">'
                    f'<div class="perry-avatar">P</div>'
                    f'<div class="perry-message">{message["content"]}</div>'
                    f'</div><div style="clear: both;"></div>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your message",
            placeholder="Type your message here... (e.g., 'I'm feeling anxious about work today')",
            height=100,
            key="perry_input",
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.perry_chat_history = [{
                'role': 'assistant',
                'content': "Chat cleared! How can I help you today?",
                'timestamp': datetime.now()
            }]
            log_user_activity(ACTIVITY_TYPES['CHAT_CLEARED'],
                            details="Perry chat history cleared")
            st.rerun()
    
    # Handle send button
    if send_button and user_input.strip():
        # Add user message to history
        st.session_state.perry_chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Log activity
        log_user_activity(ACTIVITY_TYPES['CHAT_MESSAGE_SENT'],
                        details=f"User sent message to Perry: {user_input[:50]}...")
        
        # Analyze sentiment BEFORE sending to chatbot
        sentiment_result = analyze_sentiment_for_perry(user_input)
        
        # Get Perry's response
        with st.spinner("Perry is thinking..."):
            try:
                perry_response = perry_chat(user_input)
                
                # Add Perry's response to history
                st.session_state.perry_chat_history.append({
                    'role': 'assistant',
                    'content': perry_response,
                    'timestamp': datetime.now()
                })
                
                # Log successful response
                log_user_activity(ACTIVITY_TYPES['CHAT_MESSAGE_RECEIVED'],
                                details=f"Perry responded: {perry_response[:50]}...")
                
            except Exception as e:
                error_msg = f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
                st.session_state.perry_chat_history.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'timestamp': datetime.now()
                })
                
                log_user_activity(ACTIVITY_TYPES['CHAT_ERROR'],
                                details=f"Perry chat error: {str(e)}")
        
        # Rerun to show new messages
        time.sleep(0.5)
        st.rerun()
    
    # Stats sidebar
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        message_count = len([m for m in st.session_state.perry_chat_history if m['role'] == 'user'])
        st.metric("💬 Your Messages", message_count)
    
    with col2:
        if 'perry_sentiment_logs' in st.session_state and st.session_state.perry_sentiment_logs:
            recent_sentiments = st.session_state.perry_sentiment_logs[-10:]
            positive_count = sum(1 for s in recent_sentiments if s['sentiment'] in ['POSITIVE', 'joy', 'happy'])
            st.metric("😊 Recent Positive", f"{positive_count}/10")
        else:
            st.metric("😊 Recent Positive", "N/A")
    
    with col3:
        if st.session_state.perry_chat_history:
            first_msg = st.session_state.perry_chat_history[0]['timestamp']
            duration = (datetime.now() - first_msg).total_seconds() / 60
            st.metric("⏱️ Session Time", f"{int(duration)} min")
        else:
            st.metric("⏱️ Session Time", "0 min")
    
    # Tips section
    with st.expander("💡 Tips for talking with Perry"):
        st.markdown("""
        **How to get the most from Perry:**
        
        - 🗣️ **Be open and honest** - Share your real feelings
        - 📝 **Be specific** - Describe situations and emotions in detail
        - 🤔 **Ask questions** - Perry can provide mental health insights
        - ⏰ **Check in regularly** - Track your emotional patterns over time
        - 🎯 **Set goals** - Ask Perry to help you work through challenges
        
        **Example prompts:**
        - "I'm feeling stressed about my upcoming exams"
        - "Can you help me understand why I feel anxious?"
        - "I had a great day today and want to share!"
        - "I'm struggling with motivation lately"
        """)
    
    # Disclaimer
    st.caption("⚠️ Perry is an AI companion for support and reflection. For serious mental health concerns, please consult qualified healthcare professionals.")