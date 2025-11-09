"""
Main Streamlit Application - Intelligent Study Support System
Complete Integration
"""

import streamlit as st
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from core import EmotionAnalyzer, TimerManager, StatisticsManager, TaskManager
from utils import NotificationManager, AudioManager, ThemeManager
from ui import (
    render_dashboard, 
    render_timer, 
    render_emotion_check, 
    render_analytics, 
    render_settings
)

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-# 🎓 COMPLETE INTELLIGENT STUDY SYSTEM PROJECT
## Full Folder Structure with ALL Files


