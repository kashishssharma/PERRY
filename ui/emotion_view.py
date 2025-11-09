import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render_emotion_check(emotion_analyzer, stats_manager):
    """Render the emotion check view"""
    st.markdown('<h1 class="main-header">💝 Emotional Wellness Check</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 How are you feeling?")
        st.markdown("""
        Share your thoughts, feelings, or any concerns. The AI will analyze your emotional state 
        and provide personalized support and recommendations.
        """)
        
        journal_text = st.text_area(
            "Your thoughts...",
            height=250,
            placeholder="Example: I'm feeling stressed about my upcoming exams. I have so much to study and I'm worried I won't have enough time. Sometimes I feel overwhelmed and don't know where to start...",
            help="Be honest and detailed for best results"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            analyze_btn = st.button("🔍 Analyze My Emotions", type="primary", use_container_width=True)
        
        with col_btn2:
            clear_btn = st.button("🗑️ Clear Text", use_container_width=True)
            if clear_btn:
                st.rerun()
        
        if analyze_btn:
            if journal_text.strip():
                with st.spinner("🧠 Analyzing your emotions..."):
                    result = emotion_analyzer.analyze_emotion(journal_text)
                    
                    if result:
                        st.session_state.last_emotion_result = result
                        stats_manager.add_emotion_entry(result)
                        
                        # Adaptive session adjustment
                        if st.session_state.get('adaptive_mode', True):
                            new_duration = emotion_analyzer.get_adaptive_session_adjustment(
                                result['risk_score'],
                                st.session_state.get('focus_duration', 25)
                            )
                            
                            if new_duration != st.session_state.get('focus_duration', 25):
                                old_duration = st.session_state.get('focus_duration', 25)
                                st.session_state.focus_duration = new_duration
                                st.success(f"✨ Session duration adjusted from {old_duration} to {new_duration} minutes based on your emotional state!")
                        
                        st.rerun()
            else:
                st.warning("⚠️ Please write something first!")
    
    with col2:
        st.subheader("🧠 Analysis Results")
        
        if hasattr(st.session_state, 'last_emotion_result') and st.session_state.last_emotion_result:
            result = st.session_state.last_emotion_result
            
            # Risk score display
            risk_score = result['risk_score']
            risk_color = "#fee2e2" if risk_score > 66 else "#fef3c7" if risk_score > 40 else "#d1fae5"
            risk_emoji = "🔴" if risk_score > 66 else "🟡" if risk_score > 40 else "🟢"
            risk_text = "HIGH STRESS" if risk_score > 66 else "MODERATE STRESS" if risk_score > 40 else "BALANCED STATE"
            
            st.markdown(f"""
            <div style="background: {risk_color}; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h3 style="margin: 0;">{risk_emoji} {risk_text}</h3>
                <h2 style="margin: 0.5rem 0 0 0;">Risk Score: {risk_score:.0f}/100</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            st.progress(risk_score / 100)
            
            st.markdown("---")
            
            # Detected emotions
            st.markdown("### 🎭 Detected Emotions")
            
            for emotion in result['emotions']:
                confidence_pct = emotion['confidence'] * 100
                
                with st.expander(f"{emotion['emotion'].title()} - {confidence_pct:.0f}%", expanded=True):
                    st.progress(emotion['confidence'])
                    
                    col_em1, col_em2 = st.columns(2)
                    with col_em1:
                        st.caption(f"**Risk Level:** {emotion['risk_level'].upper()}")
                    with col_em2:
                        st.caption(f"**Concern:** {emotion['concern']}")
            
            st.markdown("---")
            
            # Recommendation
            st.markdown("### 💡 Personalized Recommendation")
            st.info(result['recommendation'])
            
            # Action buttons
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("📊 View Emotion History", use_container_width=True):
                    st.session_state.active_page = "📊 Analytics"
                    st.rerun()
            
            with col_act2:
                if st.button("⏱️ Start Adapted Session", use_container_width=True):
                    st.session_state.active_page = "⏱️ Focus Timer"
                    st.rerun()
            
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #9ca3af;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">😊</div>
                <h3>No analysis yet</h3>
                <p>Share your thoughts to see your emotional analysis and get personalized recommendations.</p>
            </div>
            """, unsafe_allow_html=True)