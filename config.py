# -*- coding: utf-8 -*-
# config.py - COMPLETE FILE PART 1
# Configuration, Constants, and Utility Functions

import streamlit as st
import torch
import pandas as pd
import numpy as np
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from datetime import datetime, timedelta
import json
import os
import cv2
import threading
import time as time_module
from tensorflow.keras.models import load_model as tf_load_model  # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
from collections import defaultdict

from enhanced_notifications import (
    check_enhanced_schedule_notifications,
    handle_auto_blocking,
    show_enhanced_notifications,
    integrate_enhanced_notifications_to_schedule_manager,
    save_schedules_to_file
)

# Import website blocker functions
from website_blocker import WebsiteBlocker, show_admin_requirement, show_website_blocking_warning

# Import activity logger
from activity_logger import ActivityLogger, ACTIVITY_TYPES, log_user_activity

# Add this after your existing imports


# ============================================================================
# MENTAL HEALTH & EMOTION MAPPING
# ============================================================================
MENTAL_HEALTH_MAPPING = {
    'admiration': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'amusement': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'anger': {'risk_level': 'medium', 'concern': 'stress/aggression', 'color': 'orange'},
    'annoyance': {'risk_level': 'low', 'concern': 'mild irritation', 'color': 'yellow'},
    'approval': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'caring': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'confusion': {'risk_level': 'low', 'concern': 'cognitive uncertainty', 'color': 'yellow'},
    'curiosity': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'desire': {'risk_level': 'low', 'concern': 'motivation', 'color': 'green'},
    'disappointment': {'risk_level': 'medium', 'concern': 'mild depression', 'color': 'orange'},
    'disapproval': {'risk_level': 'low', 'concern': 'negative judgment', 'color': 'yellow'},
    'disgust': {'risk_level': 'medium', 'concern': 'aversion/stress', 'color': 'orange'},
    'embarrassment': {'risk_level': 'medium', 'concern': 'social anxiety', 'color': 'orange'},
    'excitement': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'fear': {'risk_level': 'high', 'concern': 'anxiety disorder', 'color': 'red'},
    'gratitude': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'grief': {'risk_level': 'high', 'concern': 'severe depression', 'color': 'red'},
    'joy': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'love': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'nervousness': {'risk_level': 'medium', 'concern': 'anxiety', 'color': 'orange'},
    'optimism': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'pride': {'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
    'realization': {'risk_level': 'low', 'concern': 'insight', 'color': 'green'},
    'relief': {'risk_level': 'low', 'concern': 'stress reduction', 'color': 'green'},
    'remorse': {'risk_level': 'medium', 'concern': 'guilt/regret', 'color': 'orange'},
    'sadness': {'risk_level': 'high', 'concern': 'depression', 'color': 'red'},
    'surprise': {'risk_level': 'low', 'concern': 'neutral', 'color': 'yellow'},
    'neutral': {'risk_level': 'low', 'concern': 'stable', 'color': 'green'}
}

# ============================================================================
# IMAGE EMOTION RECOGNITION
# ============================================================================

# Emotion labels for the image model
IMAGE_EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Add this FIXED version to your config.py

class ImageEmotionRecognizer:
    """Fixed class to handle background image emotion recognition"""
    
    def __init__(self, model_path='model.h5'):
        self.model = None
        self.face_cascade = None
        self.is_running = False
        self.thread = None
        self.capture_interval = 5  # seconds
        self.session_id = None
        self.capture_count = 0
        self.last_capture_time = None
        
        try:
            # Load emotion recognition model
            self.model = tf_load_model(model_path)
            print("✅ Image emotion recognition model loaded successfully")
            print(f"   Model expects input shape: {self.model.input_shape}")
            
            # Load face detector
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                print("⚠ Failed to load face cascade classifier")
                self.face_cascade = None
            else:
                print("✅ Face detector loaded successfully")
                
        except Exception as e:
            print(f"⚠ Error loading image emotion model: {str(e)}")
            self.model = None
    
    def is_available(self):
        """Check if the recognizer is ready to use"""
        return self.model is not None and self.face_cascade is not None
    
    def preprocess_face(self, face_img):
        """Preprocess face image for model prediction"""
        try:
            # Resize to model input size (48x48)
            face_img = cv2.resize(face_img, (48, 48))
            
            # Convert BGR to RGB
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            
            # Normalize pixel values to [0, 1]
            face_img = face_img.astype('float32') / 255.0
            
            # Add batch dimension
            face_img = np.expand_dims(face_img, axis=0)
            
            return face_img
            
        except Exception as e:
            print(f"❌ Error preprocessing face: {str(e)}")
            return None
    
    def start_monitoring(self, session_id):
        """Start background emotion monitoring - FIXED VERSION"""
        if self.is_running:
            print("⚠️ Monitoring already running")
            return False
        
        if not self.is_available():
            print("❌ Camera monitoring not available - model or face detector not loaded")
            return False
        
        self.session_id = session_id
        self.capture_count = 0
        self.is_running = True
        
        # Start monitoring thread
        self.thread = threading.Thread(target=self.capture_and_analyze, daemon=True)
        self.thread.start()
        
        print(f"✅ Camera monitoring started for session: {session_id}")
        
        # Log camera start
        try:
            from activity_logger import ACTIVITY_TYPES, log_user_activity
            log_user_activity(ACTIVITY_TYPES['CAMERA_STARTED'],
                             details=f"Session: {session_id}")
        except:
            pass
        
        return True
    
    def capture_and_analyze(self):
        """Background thread function to capture and analyze emotions"""
        cap = None
        session_emotions = []
        
        try:
            # Open camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Failed to open camera")
                self.is_running = False
                return
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print(f"📷 Camera monitoring started for session: {self.session_id[:20]}...")
            
            while self.is_running:
                try:
                    ret, frame = cap.read()
                    
                    if not ret:
                        print("⚠️ Failed to read frame from camera")
                        time_module.sleep(1)
                        continue
                    
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(
                        gray, 
                        scaleFactor=1.1, 
                        minNeighbors=5, 
                        minSize=(30, 30)
                    )
                    
                    if len(faces) > 0:
                        # Get the largest face
                        largest_face = max(faces, key=lambda f: f[2] * f[3])
                        x, y, w, h = largest_face
                        
                        # Extract face ROI from COLOR frame
                        face_roi = frame[y:y+h, x:x+w]
                        
                        # Preprocess
                        processed_face = self.preprocess_face(face_roi)
                        
                        if processed_face is not None and self.model is not None:
                            # Predict emotions
                            predictions = self.model.predict(processed_face, verbose=0)
                            emotion_idx = np.argmax(predictions[0])
                            confidence = float(predictions[0][emotion_idx])
                            emotion = IMAGE_EMOTION_LABELS[emotion_idx]
                            
                            # Store the emotion data
                            emotion_data = {
                                'timestamp': datetime.now(),
                                'session_id': self.session_id,
                                'emotion': emotion,
                                'confidence': confidence,
                                'source': 'camera',
                                'all_predictions': {
                                    IMAGE_EMOTION_LABELS[i]: float(predictions[0][i]) 
                                    for i in range(len(IMAGE_EMOTION_LABELS))
                                }
                            }
                            
                            # Store in temporary list
                            session_emotions.append(emotion_data)
                            
                            self.capture_count += 1
                            self.last_capture_time = datetime.now()
                            
                            print(f"📷 Capture #{self.capture_count}: {emotion} ({confidence:.2%})")
                    else:
                        if self.capture_count % 5 == 0:
                            print("⚠️ No face detected")
                    
                    # Wait for interval
                    time_module.sleep(self.capture_interval)
                    
                except Exception as e:
                    print(f"❌ Error in capture loop: {str(e)}")
                    time_module.sleep(1)
        
        except Exception as e:
            print(f"❌ Critical error in capture loop: {str(e)}")
        
        finally:
            if cap is not None:
                cap.release()
            
            # Save to temporary file
            print(f"📷 Saving {len(session_emotions)} emotions...")
            
            import pickle
            temp_file = f"temp_emotions_{self.session_id}.pkl"
            try:
                with open(temp_file, 'wb') as f:
                    pickle.dump({
                        'session_id': self.session_id,
                        'emotions': session_emotions,
                        'count': len(session_emotions)
                    }, f)
                print(f"✅ Saved {len(session_emotions)} emotions to {temp_file}")
            except Exception as e:
                print(f"❌ Error saving emotions: {str(e)}")
            
            print(f"📷 Camera monitoring stopped. Session captures: {self.capture_count}")
    
    def stop_monitoring(self):
        """Stop background emotion monitoring"""
        if not self.is_running:
            return False
        
        print("🛑 Stopping camera monitoring...")
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        # Load emotions from temp file
        import pickle
        temp_file = f"temp_emotions_{self.session_id}.pkl"
        
        emotions_loaded = []
        try:
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    data = pickle.load(f)
                
                emotions_loaded = data['emotions']
                print(f"✅ Loaded {len(emotions_loaded)} emotions from file")
                
                # Clean up temp file
                os.remove(temp_file)
                print(f"🗑️ Cleaned up {temp_file}")
            else:
                print(f"⚠️ Temp file not found: {temp_file}")
        except Exception as e:
            print(f"❌ Error loading emotions: {str(e)}")
        
        print(f"✅ Monitoring stopped. Total captures: {self.capture_count}")
        
        # Log camera stop
        try:
            from activity_logger import ACTIVITY_TYPES, log_user_activity
            log_user_activity(ACTIVITY_TYPES['CAMERA_STOPPED'],
                             details=f"Session: {self.session_id}, Captures: {self.capture_count}")
        except:
            pass
        
        return emotions_loaded  # Return the emotions list
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'is_available': self.is_available(),
            'session_id': self.session_id,
            'capture_count': self.capture_count,
            'last_capture': self.last_capture_time
        }

def get_session_image_emotions(session_id):
    """Get all image emotions for a specific session - IMPROVED MATCHING"""
    if 'image_emotions' not in st.session_state:
        return []
    
    if not session_id:
        return []
    
    # Debug: Print what we're looking for
    print(f"🔍 Looking for emotions with session_id: {session_id}")
    
    # Try exact match first
    exact_matches = [
        e for e in st.session_state.image_emotions 
        if e.get('session_id') == session_id
    ]
    
    if exact_matches:
        print(f"✅ Found {len(exact_matches)} emotions with exact match")
        return exact_matches
    
    # Try partial match (first 20 characters)
    partial_matches = [
        e for e in st.session_state.image_emotions 
        if e.get('session_id', '')[:20] == session_id[:20]
    ]
    
    if partial_matches:
        print(f"✅ Found {len(partial_matches)} emotions with partial match")
        return partial_matches
    
    print(f"❌ No emotions found for session: {session_id[:30]}...")
    return []


def get_image_emotion_summary(session_id=None):
    """Get summary statistics for image emotions - IMPROVED"""
    if session_id is None:
        # Get ALL emotions
        emotions = st.session_state.get('image_emotions', [])
        print(f"📊 Getting summary for ALL emotions: {len(emotions)} total")
    else:
        # Get emotions for specific session
        emotions = get_session_image_emotions(session_id)
        print(f"📊 Getting summary for session {session_id[:30]}...: {len(emotions)} emotions")
    
    if not emotions:
        print("⚠ No emotions to summarize")
        return None
    
    # Count emotions
    from collections import defaultdict
    emotion_counts = defaultdict(int)
    risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
    
    for emotion_data in emotions:
        emotion = emotion_data.get('emotion', 'Unknown')
        emotion_counts[emotion] += 1
        
        # Map image emotions to risk levels
        risk_level = get_image_emotion_risk_level(emotion)
        risk_distribution[risk_level] += 1
    
    # Find dominant emotion
    if emotion_counts:
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
    else:
        dominant_emotion = 'Neutral'
    
    summary = {
        'total_captures': len(emotions),
        'emotion_counts': dict(emotion_counts),
        'dominant_emotion': dominant_emotion,
        'risk_distribution': risk_distribution
    }
    
    print(f"✅ Summary created: {summary}")
    return summary


def get_all_sessions_with_image_data():
    """Get all focus sessions that have image emotion data - IMPROVED"""
    if 'focus_sessions' not in st.session_state:
        print("⚠ No focus sessions in session state")
        return []
    
    if 'image_emotions' not in st.session_state:
        print("⚠ No image emotions in session state")
        return []
    
    print(f"📊 Analyzing {len(st.session_state.focus_sessions)} focus sessions")
    print(f"📊 Total image emotions available: {len(st.session_state.image_emotions)}")
    
    # Debug: Show all unique session IDs in image_emotions
    unique_session_ids = set(e.get('session_id', 'N/A') for e in st.session_state.image_emotions)
    print(f"📊 Unique session IDs in emotions: {len(unique_session_ids)}")
    for sid in list(unique_session_ids)[:5]:
        print(f"   - {sid[:50]}...")
    
    sessions_with_data = []
    
    for idx, session in enumerate(st.session_state.focus_sessions):
        if not session.get('completed'):
            continue
        
        # Get session_id - THIS IS CRITICAL
        session_id = session.get('session_id')
        
        if not session_id:
            # Create fallback ID based on timestamp
            print(f"⚠ Session {idx} has no session_id, creating fallback")
            session_id = f"session_{session['date'].timestamp()}"
            session['session_id'] = session_id  # Save it back
        
        print(f"🔍 Checking session {idx}: {session_id[:50]}...")
        
        # Get emotions for this session
        session_emotions = get_session_image_emotions(session_id)
        
        if session_emotions:
            print(f"✅ Found {len(session_emotions)} emotions for session {idx}")
            summary = get_image_emotion_summary(session_id)
            
            if summary:
                sessions_with_data.append({
                    'session': session,
                    'summary': summary,
                    'image_count': len(session_emotions),
                    'start_time': session['date']
                })
        else:
            print(f"❌ No emotions found for session {idx}")
    
    print(f"✅ Total sessions with camera data: {len(sessions_with_data)}")
    return sessions_with_data


def get_image_emotion_risk_level(emotion):
    """Map image emotions to risk levels"""
    risk_mapping = {
        'Angry': 'high',
        'Disgust': 'medium',
        'Fear': 'high',
        'Happy': 'low',
        'Sad': 'high',
        'Surprise': 'low',
        'Neutral': 'low'
    }
    return risk_mapping.get(emotion, 'low')


# ============================================================================
# ADD THIS DEBUG FUNCTION TO YOUR CONFIG.PY
# ============================================================================

def debug_camera_data():
    """
    Debug function to analyze camera emotion data
    """
    import streamlit as st
    
    st.write("### 🔧 Camera Data Debug Information")
    
    # Check if data exists
    if 'image_emotions' not in st.session_state:
        st.error("❌ No 'image_emotions' in session state")
        return
    
    total_emotions = len(st.session_state.image_emotions)
    st.write(f"*Total emotions captured:* {total_emotions}")
    
    if total_emotions == 0:
        st.warning("⚠ No emotions captured yet")
        return
    
    # Show sample data
    st.write("*Sample emotion data (first 3):*")
    for i, emotion in enumerate(st.session_state.image_emotions[:3]):
        st.json({
            'index': i,
            'emotion': emotion.get('emotion'),
            'confidence': emotion.get('confidence'),
            'session_id': emotion.get('session_id', 'N/A')[:50] + '...',
            'timestamp': str(emotion.get('timestamp'))
        })
    
    # Show unique session IDs in emotions
    unique_emotion_session_ids = set(e.get('session_id', 'MISSING') for e in st.session_state.image_emotions)
    st.write(f"*Unique session IDs in emotions:* {len(unique_emotion_session_ids)}")
    for sid in list(unique_emotion_session_ids)[:5]:
        st.code(sid[:80] + ('...' if len(sid) > 80 else ''))
    
    # Check focus sessions
    if 'focus_sessions' not in st.session_state:
        st.error("❌ No 'focus_sessions' in session state")
        return
    
    st.write(f"*Total focus sessions:* {len(st.session_state.focus_sessions)}")
    
    completed_sessions = [s for s in st.session_state.focus_sessions if s.get('completed')]
    st.write(f"*Completed sessions:* {len(completed_sessions)}")
    
    # Show session IDs from focus sessions
    st.write("*Session IDs from completed focus sessions:*")
    for i, session in enumerate(completed_sessions[:5]):
        session_id = session.get('session_id', 'MISSING')
        st.code(f"Session {i}: {session_id[:80]}...")
    
    # Try to match
    st.write("🔍 Matching Analysis:")
    for i, session in enumerate(completed_sessions[:3]):
        session_id = session.get('session_id', 'MISSING')
        
        # Count matches
        exact_matches = [e for e in st.session_state.image_emotions if e.get('session_id') == session_id]
        
        if exact_matches:
            st.success(f"✅ Session {i}: Found {len(exact_matches)} emotions")
        else:
            st.error(f"❌ Session {i}: No emotions found")
            st.caption(f"Looking for: {session_id[:60]}...")
    
    # Show emotion session IDs vs focus session IDs side by side
    st.write("📊 Side-by-Side Comparison:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("*Session IDs in Emotions:*")
        for sid in list(unique_emotion_session_ids)[:3]:
            st.text(sid[:60])
    
    with col2:
        st.write("*Session IDs in Focus Sessions:*")
        for session in completed_sessions[:3]:
            sid = session.get('session_id', 'MISSING')
            st.text(sid[:60])


# Test function to verify preprocessing
def test_image_emotion_recognizer():
    """
    Test function to verify the emotion recognizer works correctly
    Run this to test before using in the app
    """
    print("=" * 60)
    print("TESTING IMAGE EMOTION RECOGNIZER")
    print("=" * 60)
    
    recognizer = ImageEmotionRecognizer()
    
    print(f"\n1. Model available: {recognizer.is_available()}")
    
    if recognizer.model:
        print(f"2. Model input shape: {recognizer.model.input_shape}")
        print(f"3. Model output shape: {recognizer.model.output_shape}")
        
        # Create a dummy RGB image (simulating camera frame)
        dummy_face = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        print(f"\n4. Test input shape (BGR from camera): {dummy_face.shape}")
        
        # Test preprocessing
        processed = recognizer.preprocess_face(dummy_face)
        
        if processed is not None:
            print(f"5. Preprocessed shape: {processed.shape}")
            print(f"6. Preprocessed dtype: {processed.dtype}")
            print(f"7. Preprocessed range: [{processed.min():.3f}, {processed.max():.3f}]")
            
            # Test prediction
            try:
                prediction = recognizer.model.predict(processed, verbose=0)
                print(f"\n✅ PREDICTION SUCCESSFUL!")
                print(f"8. Output shape: {prediction.shape}")
                print(f"9. Probabilities sum: {prediction.sum():.4f} (should be ~1.0)")
                
                # Show predicted emotion
                emotion_idx = np.argmax(prediction[0])
                confidence = prediction[0][emotion_idx]
                emotion = IMAGE_EMOTION_LABELS[emotion_idx]
                
                print(f"\n10. Predicted emotion: {emotion}")
                print(f"11. Confidence: {confidence:.2%}")
                
                print("\n" + "=" * 60)
                print("✅ ALL TESTS PASSED - READY TO USE!")
                print("=" * 60)
                
            except Exception as e:
                print(f"\n❌ PREDICTION FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Preprocessing failed")
    else:
        print("❌ Model not loaded")

if __name__ == "_main_":
    test_image_emotion_recognizer()

# ============================================================================
# MOTIVATIONAL QUOTES
# ============================================================================
MOTIVATIONAL_QUOTES = [
    "You are capable of amazing things. Keep going! 💪",
    "Every small step forward is progress. Be proud! 🎯",
    "Your mental health matters. Take care of yourself. 💚",
    "Focus on progress, not perfection. 🎨",
    "You've got this! One day at a time. 💪",
    "Believe in yourself and your journey. 🌟",
    "Your effort today builds your success tomorrow. 📈",
    "Rest is productive too. Honor your needs. 🧘",
    "Celebrate small wins - they add up! 🎉",
    "You're stronger than you think. Keep pushing! 💪"
]

# ============================================================================
# BLOCKED WEBSITES
# ============================================================================
BLOCKED_SITES = [
    'youtube.com', 'www.youtube.com',
    'instagram.com', 'www.instagram.com',
    'facebook.com', 'www.facebook.com',
    'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
    'reddit.com', 'www.reddit.com',
    'netflix.com', 'www.netflix.com',
    'twitch.tv', 'www.twitch.tv',
    'tiktok.com', 'www.tiktok.com'
]

# -*- coding: utf-8 -*-
# config.py - COMPLETE FILE PART 2
# CSS Styling and Core Functions

# ============================================================================
# CUSTOM CSS FUNCTION
# ============================================================================

def get_custom_css(dark_mode=False):
    """Get custom CSS based on theme with enhanced dark mode support"""
    
    # Base CSS that applies to both themes
    base_css = """
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .risk-high {
        border-left: 5px solid #f44336;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .risk-medium {
        border-left: 5px solid #ff9800;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .risk-low {
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .timer-display {
        font-size: 4rem;
        font-weight: bold;
        text-align: center;
        font-family: 'Courier New', monospace;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .quote-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-style: italic;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .streak-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
    }
    
    .session-card {
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .session-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .blocking-active {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.85; transform: scale(0.98); }
    }
    
    .camera-active {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        font-size: 0.9rem;
        animation: pulse 2s infinite;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
    }
    
    .journal-entry-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .journal-entry-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .journal-entry-date {
        font-weight: bold;
        color: #667eea;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .journal-entry-text {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }
    
    .emotion-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    .schedule-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .schedule-card:hover {
        transform: translateX(5px);
    }
    
    .schedule-card.priority-high {
        border-left-color: #f44336;
    }
    
    .schedule-card.priority-medium {
        border-left-color: #ff9800;
    }
    
    .schedule-card.priority-low {
        border-left-color: #4caf50;
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    </style>
    """
    
    # Light theme specific CSS
    light_theme_css = """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
    }
    
    .timer-display {
        color: #667eea;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .session-card {
        background: white;
    }
    
    .journal-entry-card {
        background: white;
    }
    
    .journal-entry-text {
        background: rgba(102, 126, 234, 0.05);
        color: #333;
    }
    
    .schedule-card {
        background: white;
    }
    </style>
    """
    
    # Dark theme specific CSS
    dark_theme_css = """
    <style>
    .main-header {
        background: linear-gradient(135deg, #8b9dff 0%, #a076d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .metric-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    .risk-high {
        background: linear-gradient(135deg, #4a1a1a 0%, #3a1515 100%);
        border-left: 5px solid #ff6b6b;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #4a3a1a 0%, #3a2e15 100%);
        border-left: 5px solid #ffa726;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #1a4a2e 0%, #153a23 100%);
        border-left: 5px solid #66bb6a;
    }
    
    .timer-display {
        color: #8b9dff;
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border: 2px solid rgba(139, 157, 255, 0.3);
        box-shadow: 0 4px 20px rgba(139, 157, 255, 0.2);
    }
    
    .session-card {
        background: #2d3748;
        border-left: 4px solid #8b9dff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .session-card:hover {
        background: #344155;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    
    .journal-entry-card {
        background: #2d3748;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .journal-entry-card:hover {
        background: #344155;
        border: 1px solid rgba(102, 126, 234, 0.4);
    }
    
    .journal-entry-date {
        color: #8b9dff;
    }
    
    .journal-entry-text {
        background: rgba(102, 126, 234, 0.15);
        color: #e2e8f0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .schedule-card {
        background: #2d3748;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .schedule-card:hover {
        background: #344155;
    }
    
    .emotion-tag {
        background: rgba(102, 126, 234, 0.2);
        color: #a0aec0;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .quote-box {
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }
    
    ::-webkit-scrollbar-track {
        background: #1a202c;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4a5568;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #667eea;
    }
    
    .stMarkdown, .stText {
        color: #e2e8f0;
    }
    
    a {
        color: #8b9dff;
    }
    
    a:hover {
        color: #a076d4;
    }
    
    hr {
        border-color: rgba(102, 126, 234, 0.2);
    }
    
    .element-container .stAlert {
        background: rgba(45, 55, 72, 0.8);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .dataframe {
        background: #2d3748;
        color: #e2e8f0;
    }
    
    .dataframe th {
        background: #1a202c;
        color: #8b9dff;
    }
    
    .dataframe td {
        border-color: rgba(102, 126, 234, 0.2);
    }
    
    input, textarea, select {
        background: #2d3748 !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border: 1px solid rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3) !important;
    }
    </style>
    """
    
    if dark_mode:
        return base_css + dark_theme_css
    else:
        return base_css + light_theme_css

# ============================================================================
# MODEL LOADING
# ============================================================================
@st.cache_resource
def load_model():
    """Load the trained RoBERTa model and tokenizer"""
    try:
        model_path = "emotion_roberta_model"
        
        if not os.path.exists(model_path):
            st.warning(f"⚠️ Model not found at: {model_path}")
            st.info("ℹ️ Using demo mode - update model_path to use your trained model")
            return None, None, None
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = RobertaForSequenceClassification.from_pretrained(model_path).to(device)
        tokenizer = RobertaTokenizer.from_pretrained(model_path)
        
        labels_path = os.path.join(os.path.dirname(model_path), "emotion_labels.json")
        if os.path.exists(labels_path):
            with open(labels_path, 'r') as f:
                emotion_labels = json.load(f)
        else:
            emotion_labels = list(MENTAL_HEALTH_MAPPING.keys())
        
        return model, tokenizer, emotion_labels
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

# ============================================================================
# TEXT PROCESSING FUNCTIONS
# ============================================================================
def clean_text(text):
    """Clean and preprocess text"""
    if pd.isna(text) or text == "":
        return ""
    text = ' '.join(text.split())
    return text.strip()

def predict_emotions_multilabel(text, model, tokenizer, emotion_labels, top_k=5):
    """Predict multiple emotions with confidence scores"""
    if model is None:
        return [
            {'emotion': 'neutral', 'confidence': 0.75, 'risk_level': 'low', 'concern': 'stable', 'color': 'green'},
            {'emotion': 'optimism', 'confidence': 0.15, 'risk_level': 'low', 'concern': 'positive', 'color': 'green'},
        ]
    
    text = clean_text(text)
    if not text:
        return []
    
    device = next(model.parameters()).device
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    ).to(device)
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    top_probs, top_indices = torch.topk(predictions[0], k=min(top_k, len(emotion_labels)))
    
    results = []
    for prob, idx in zip(top_probs, top_indices):
        emotion = emotion_labels[idx.item()]
        results.append({
            'emotion': emotion,
            'confidence': prob.item(),
            'risk_level': MENTAL_HEALTH_MAPPING.get(emotion, {}).get('risk_level', 'low'),
            'concern': MENTAL_HEALTH_MAPPING.get(emotion, {}).get('concern', 'unknown'),
            'color': MENTAL_HEALTH_MAPPING.get(emotion, {}).get('color', 'gray')
        })
    
    return results

def calculate_risk_score(emotions_data):
    """Calculate overall mental health risk score"""
    risk_weights = {'high': 3, 'medium': 2, 'low': 1}
    total_score = sum(risk_weights[e['risk_level']] * e['confidence'] for e in emotions_data)
    max_score = sum(risk_weights['high'] * e['confidence'] for e in emotions_data)
    
    if max_score == 0:
        return 0
    
    return (total_score / max_score) * 100

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def format_time(seconds):
    """Format seconds to MM:SS"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def calculate_study_streak():
    """Calculate consecutive days with study sessions"""
    if 'focus_sessions' not in st.session_state or not st.session_state.focus_sessions:
        return 0
    
    sessions = sorted(st.session_state.focus_sessions, key=lambda x: x['date'], reverse=True)
    streak = 1
    current_date = sessions[0]['date'].date()
    
    for session in sessions[1:]:
        session_date = session['date'].date()
        if (current_date - session_date).days == 1:
            streak += 1
            current_date = session_date
        elif (current_date - session_date).days > 1:
            break
    
    return streak

def get_today_focus_time():
    """Get total focus time for today in minutes"""
    if 'focus_sessions' not in st.session_state:
        return 0
    
    today = datetime.now().date()
    total_seconds = sum(
        s['duration'] for s in st.session_state.focus_sessions 
        if s['date'].date() == today and s['completed']
    )
    return total_seconds // 60

def initialize_session_state():
    """Initialize all session state variables"""
    # Camera monitoring states
    if 'camera_monitoring' not in st.session_state:
        st.session_state.camera_monitoring = False
    
    if 'image_recognizer' not in st.session_state:
        st.session_state.image_recognizer = ImageEmotionRecognizer()
    
    if 'image_emotions' not in st.session_state:
        st.session_state.image_emotions = []
    
    # Journal/Emotion tracking
    if 'emotion_history' not in st.session_state:
        st.session_state.emotion_history = []
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0
    
    # Focus session tracking
    if 'focus_sessions' not in st.session_state:
        st.session_state.focus_sessions = []
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_seconds' not in st.session_state:
        st.session_state.timer_seconds = 0
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    if 'blocking_active' not in st.session_state:
        st.session_state.blocking_active = False
    
    # Initialize website blocker
    if 'website_blocker' not in st.session_state:
        st.session_state.website_blocker = WebsiteBlocker(blocked_sites=BLOCKED_SITES)
    
    # Schedule tracking
    if 'schedules' not in st.session_state:
        st.session_state.schedules = []
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'last_notification_check' not in st.session_state:
        st.session_state.last_notification_check = datetime.now()
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard Overview"
    
    # Dark mode
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Activity logger
    if 'activity_logger' not in st.session_state:
        st.session_state.activity_logger = ActivityLogger()
    if 'image_emotions' not in st.session_state:
        st.session_state.image_emotions = []
        print("✅ Initialized image_emotions list in session state")

        # -*- coding: utf-8 -*-
# config.py - COMPLETE FILE PART 3
# Schedule Management Functions

# ============================================================================
# SCHEDULE FUNCTIONS
# ============================================================================
def check_schedule_conflict(new_start, new_end, new_date, exclude_id=None):
    """Check if a new schedule conflicts with existing schedules"""
    conflicts = []
    for schedule in st.session_state.schedules:
        if exclude_id and schedule.get('id') == exclude_id:
            continue
        
        if schedule['date'] == new_date:
            existing_start = schedule['start_time']
            existing_end = schedule['end_time']
            
            if (new_start < existing_end and new_end > existing_start):
                conflicts.append(schedule)
    
    return conflicts

def add_schedule(title, description, date, start_time, end_time, category, priority):
    """Add a new schedule"""
    schedule_id = f"schedule_{len(st.session_state.schedules)}_{datetime.now().timestamp()}"
    
    schedule = {
        'id': schedule_id,
        'title': title,
        'description': description,
        'date': date,
        'start_time': start_time,
        'end_time': end_time,
        'category': category,
        'priority': priority,
        'completed': False,
        'created_at': datetime.now(),
        'started': False,
        'missed_notified': False
    }
    
    st.session_state.schedules.append(schedule)
    save_schedules_for_background_service()
    save_schedules_to_file()
    return schedule_id

def update_schedule(schedule_id, **kwargs):
    """Update an existing schedule"""
    for schedule in st.session_state.schedules:
        if schedule['id'] == schedule_id:
            schedule.update(kwargs)
            save_schedules_to_file()
            return True
    return False

def delete_schedule(schedule_id):
    """Delete a schedule"""
    st.session_state.schedules = [s for s in st.session_state.schedules if s['id'] != schedule_id]
    save_schedules_to_file()

def get_schedule_by_id(schedule_id):
    """Get a specific schedule by ID"""
    for schedule in st.session_state.schedules:
        if schedule['id'] == schedule_id:
            return schedule
    return None

def get_today_schedules():
    """Get all schedules for today"""
    today = datetime.now().date()
    return [s for s in st.session_state.schedules if s['date'] == today]

def get_upcoming_schedules(days=7):
    """Get schedules for the next N days"""
    today = datetime.now().date()
    future_date = today + timedelta(days=days)
    return [s for s in st.session_state.schedules 
            if today <= s['date'] <= future_date]

def get_schedule_stats():
    """Get statistics about schedules"""
    total = len(st.session_state.schedules)
    completed = sum(1 for s in st.session_state.schedules if s['completed'])
    today_count = len(get_today_schedules())
    
    return {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'today': today_count
    }

def get_unread_notifications():
    """
    Get unread notifications count
    Used for displaying notification badge in sidebar
    """
    if 'notifications' not in st.session_state:
        return []
    return [n for n in st.session_state.notifications if not n.get('read', False)]

# ============================================================================
# ENHANCED SCHEDULE NOTIFICATIONS
# ============================================================================
def check_schedule_notifications_enhanced():
    """
    Enhanced notification system with blocking for missed schedules
    Returns: list of notifications with actions
    """
    now = datetime.now()
    today = now.date()
    
    # Check every minute
    if (now - st.session_state.last_notification_check).seconds < 60:
        return []
    
    st.session_state.last_notification_check = now
    new_notifications = []
    
    for schedule in st.session_state.schedules:
        if schedule['completed'] or schedule['date'] != today:
            continue
        
        # Calculate time difference
        schedule_datetime = datetime.combine(schedule['date'], schedule['start_time'])
        time_diff = (schedule_datetime - now).total_seconds() / 60  # in minutes
        
        # Check if schedule has already passed and not started
        if time_diff < -15:  # 15 minutes past start time
            # Mark as missed if not already done
            if not schedule.get('missed_notified', False):
                notification = {
                    'id': f"missed_{schedule['id']}",
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': 'missed',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'action': 'block_sites'
                }
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
                schedule['missed_notified'] = True
                
                # Log the missed schedule
                log_user_activity(ACTIVITY_TYPES['SCHEDULE_MISSED'], 
                                details=f"Missed: {schedule['title']}",
                                metadata={'schedule_id': schedule['id']})
        
        # 10 minutes before
        elif 9 <= time_diff <= 11:
            notification_id = f"notif_10min_{schedule['id']}"
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': '10min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"⏰ Upcoming: {schedule['title']} starts in 10 minutes!"
                }
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
        
        # 5 minutes before
        elif 4 <= time_diff <= 6:
            notification_id = f"notif_5min_{schedule['id']}"
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': '5min_warning',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"⚠️ Starting Soon: {schedule['title']} in 5 minutes! Get ready! 💪"
                }
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
        
        # At start time
        elif -1 <= time_diff <= 1:
            notification_id = f"notif_start_{schedule['id']}"
            if not any(n['id'] == notification_id for n in st.session_state.notifications):
                notification = {
                    'id': notification_id,
                    'schedule_id': schedule['id'],
                    'title': schedule['title'],
                    'type': 'start_now',
                    'time': schedule['start_time'],
                    'time_diff': time_diff,
                    'timestamp': now,
                    'read': False,
                    'message': f"🔔 Starting Now: {schedule['title']}! Time to focus! 🎯"
                }
                st.session_state.notifications.append(notification)
                new_notifications.append(notification)
    
    return new_notifications

def get_motivational_message_for_schedule(schedule):
    """Get motivational message based on schedule priority and category"""
    import random
    
    messages = {
        'Urgent': [
            "🚨 This is urgent! You've got this!",
            "⚡ Time to tackle this important task!",
            "💪 Show this task who's boss!"
        ],
        'High': [
            "🎯 High priority - let's crush it!",
            "🔥 Important work ahead - you're ready!",
            "⭐ This matters - give it your best!"
        ],
        'Medium': [
            "👍 Time to get things done!",
            "✨ Let's make progress on this!",
            "🎨 Ready to be productive?"
        ],
        'Low': [
            "📝 A small task to cross off!",
            "✓ Quick win coming up!",
            "🌟 Easy progress ahead!"
        ]
    }
    
    priority = schedule.get('priority', 'Medium')
    return random.choice(messages.get(priority, messages['Medium']))

def handle_missed_schedule(schedule, blocker):
    """Handle a missed schedule by blocking distracting sites"""
    result = {
        'blocked': False,
        'message': '',
        'motivation': ''
    }
    
    # Check if blocker has admin privileges
    if not blocker._check_admin_privileges():
        result['message'] = "⚠️ Cannot block sites - admin privileges required"
        return result
    
    # Block websites
    block_result = blocker.block_websites(enable_smart_blocking=True)
    
    if block_result['success']:
        result['blocked'] = True
        result['message'] = f"🚫 Blocked {len(block_result['blocked_sites'])} distracting sites to help you focus!"
        result['motivation'] = get_motivational_message_for_schedule(schedule)
        
        # Log the blocking action
        log_user_activity(ACTIVITY_TYPES['BLOCKING_BY_SCHEDULE'],
                        details=f"Auto-blocked for missed schedule: {schedule['title']}",
                        metadata={'schedule_id': schedule['id']})
    else:
        result['message'] = "⚠️ Could not enable blocking"
    
    return result


# At the end of config.py, add this function:

def save_schedules_for_background_service():
    """Save schedules to file for background notification service"""
    import pickle
    try:
        with open('schedules_data.pkl', 'wb') as f:
            pickle.dump(st.session_state.schedules, f)
    except Exception as e:
        print(f"Error saving schedules for background service: {e}")

# ============================================================================
# PERRY CHATBOT INTEGRATION & SENTIMENT ANALYSIS
# ============================================================================

# Initialize sentiment analyzer (cached to load only once)
@st.cache_resource
def load_sentiment_analyzer():
    """Load sentiment analysis pipeline"""
    try:
        from transformers import pipeline
        # Use a more detailed sentiment model
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        return sentiment_analyzer
    except Exception as e:
        print(f"⚠️ Could not load advanced sentiment model: {e}")
        # Fallback to default model
        try:
            from transformers import pipeline
            return pipeline("sentiment-analysis")
        except:
            return None

def analyze_sentiment_for_perry(message: str):
    """
    Analyze sentiment of user message
    Returns: dict with sentiment label and score
    """
    try:
        sentiment_analyzer = load_sentiment_analyzer()
        
        if sentiment_analyzer is None:
            # Fallback: simple keyword-based sentiment
            positive_words = ['happy', 'good', 'great', 'excellent', 'wonderful', 'joy', 'love', 'excited']
            negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'angry', 'depressed', 'anxious']
            
            message_lower = message.lower()
            pos_count = sum(1 for word in positive_words if word in message_lower)
            neg_count = sum(1 for word in negative_words if word in message_lower)
            
            if pos_count > neg_count:
                sentiment = 'POSITIVE'
                score = min(0.9, 0.6 + (pos_count * 0.1))
            elif neg_count > pos_count:
                sentiment = 'NEGATIVE'
                score = min(0.9, 0.6 + (neg_count * 0.1))
            else:
                sentiment = 'NEUTRAL'
                score = 0.5
        else:
            # Use transformer model
            result = sentiment_analyzer(message[:512])[0]  # Limit to 512 chars
            sentiment = result['label']
            score = result['score']
            
            # Normalize label names
            if sentiment in ['LABEL_0', 'negative', 'NEG']:
                sentiment = 'NEGATIVE'
            elif sentiment in ['LABEL_1', 'neutral', 'NEU']:
                sentiment = 'NEUTRAL'
            elif sentiment in ['LABEL_2', 'positive', 'POS']:
                sentiment = 'POSITIVE'
        
        # Store sentiment log
        sentiment_data = {
            'id': f"sentiment_{datetime.now().timestamp()}",
            'timestamp': datetime.now(),
            'user_message': message,
            'sentiment': sentiment,
            'sentiment_score': float(score)
        }
        
        # Initialize sentiment logs if not exists
        if 'perry_sentiment_logs' not in st.session_state:
            st.session_state.perry_sentiment_logs = []
        
        # Add to logs
        st.session_state.perry_sentiment_logs.append(sentiment_data)
        
        print(f"✅ Sentiment analyzed: {sentiment} ({score:.2f})")
        
        return sentiment_data
        
    except Exception as e:
        print(f"❌ Sentiment analysis error: {e}")
        return {
            'id': f"sentiment_{datetime.now().timestamp()}",
            'timestamp': datetime.now(),
            'user_message': message,
            'sentiment': 'NEUTRAL',
            'sentiment_score': 0.5
        }

def perry_chat(message: str) -> str:
    """
    Send message to Perry chatbot and get response
    Ensures Perry identifies as Perry, not Sahaj
    """
    try:
        from gradio_client import Client
        
        # Create instruction to override name
        system_instruction = (
            "From now on, your name is Perry. You are a compassionate mental health companion. "
            "You provide emotional support, listen actively, and help users process their feelings. "
            "Never say you are Sahaj or any other name. Always respond as Perry. "
            "Be empathetic, warm, and supportive.\n\n"
            f"User message: {message}"
        )
        
        # Connect to the chatbot API
        client = Client("SENTIBOT2705/mentalhealthbot-phi2")
        
        # Call the API
        response = client.predict(
            message=system_instruction,
            api_name="/chat"
        )
        
        # Extract response text
        if isinstance(response, str):
            bot_response = response
        elif isinstance(response, (list, tuple)) and len(response) > 0:
            bot_response = response[0]
        else:
            bot_response = str(response)
        
        # Post-process to replace any "Sahaj" mentions with "Perry"
        bot_response = bot_response.replace("Sahaj", "Perry")
        bot_response = bot_response.replace("sahaj", "Perry")
        bot_response = bot_response.replace("SAHAJ", "PERRY")
        
        # If response is too short or empty, provide fallback
        if len(bot_response.strip()) < 10:
            bot_response = "I'm here to listen. Can you tell me more about how you're feeling?"
        
        return bot_response
        
    except Exception as e:
        print(f"❌ Perry chat API error: {e}")
        
        # Fallback responses based on simple keyword matching
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'stress']):
            return ("I understand that anxiety can feel overwhelming. Remember, it's okay to feel this way. "
                   "Try taking some deep breaths with me. What's been weighing on your mind?")
        
        elif any(word in message_lower for word in ['sad', 'depressed', 'down', 'unhappy']):
            return ("I hear that you're going through a tough time. Your feelings are valid. "
                   "Would you like to talk about what's been making you feel this way?")
        
        elif any(word in message_lower for word in ['happy', 'great', 'excited', 'good']):
            return ("That's wonderful to hear! I'm so glad you're feeling positive. "
                   "What's been going well for you?")
        
        else:
            return ("I'm here to listen and support you. Can you tell me more about what's on your mind? "
                   "Remember, there's no judgment here – just support.")

def get_sentiment_trend_data():
    """
    Get sentiment trend data for analytics
    Returns: DataFrame with timestamps and sentiment scores
    """
    if 'perry_sentiment_logs' not in st.session_state or not st.session_state.perry_sentiment_logs:
        return None
    
    import pandas as pd
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.perry_sentiment_logs)
    
    # Map sentiment to numerical score for plotting
    sentiment_map = {
        'POSITIVE': 1,
        'NEUTRAL': 0,
        'NEGATIVE': -1
    }
    
    df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)
    
    # Adjust score based on sentiment direction
    df['adjusted_score'] = df.apply(
        lambda row: row['sentiment_score'] if row['sentiment_numeric'] >= 0 
                    else -row['sentiment_score'],
        axis=1
    )
    
    return df

# Add to activity types if not already there
if 'CHAT_MESSAGE_SENT' not in ACTIVITY_TYPES:
    ACTIVITY_TYPES['CHAT_MESSAGE_SENT'] = 'chat_message_sent'
if 'CHAT_MESSAGE_RECEIVED' not in ACTIVITY_TYPES:
    ACTIVITY_TYPES['CHAT_MESSAGE_RECEIVED'] = 'chat_message_received'
if 'CHAT_ERROR' not in ACTIVITY_TYPES:
    ACTIVITY_TYPES['CHAT_ERROR'] = 'chat_error'
if 'CHAT_CLEARED' not in ACTIVITY_TYPES:
    ACTIVITY_TYPES['CHAT_CLEARED'] = 'chat_cleared'