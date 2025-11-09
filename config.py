"""
Configuration settings for the Intelligent Study System
"""

import os
from datetime import datetime

# Application Settings
APP_NAME = "Intelligent Study Support System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-Powered Focus & Emotional Wellness Platform"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
SOUNDS_DIR = os.path.join(RESOURCES_DIR, "sounds")
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
THEMES_DIR = os.path.join(RESOURCES_DIR, "themes")

# Create directories
for directory in [DATA_DIR, MODEL_DIR, RESOURCES_DIR, SOUNDS_DIR, IMAGES_DIR, THEMES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Model Settings
EMOTION_MODEL = "SamLowe/roberta-base-go_emotions"
MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model")

# Timer Settings
DEFAULT_FOCUS_TIME = 25
DEFAULT_SHORT_BREAK = 5
DEFAULT_LONG_BREAK = 15
SESSIONS_BEFORE_LONG_BREAK = 4

# Emotion Risk Mapping
EMOTION_RISK_MAP = {
    'admiration': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'amusement': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'anger': {'risk': 'medium', 'concern': 'stress/aggression', 'color': '#f59e0b'},
    'annoyance': {'risk': 'low', 'concern': 'mild irritation', 'color': '#fbbf24'},
    'approval': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'caring': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'confusion': {'risk': 'low', 'concern': 'cognitive uncertainty', 'color': '#fbbf24'},
    'curiosity': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'desire': {'risk': 'low', 'concern': 'motivation', 'color': '#10b981'},
    'disappointment': {'risk': 'medium', 'concern': 'mild depression', 'color': '#f59e0b'},
    'disapproval': {'risk': 'low', 'concern': 'negative judgment', 'color': '#fbbf24'},
    'disgust': {'risk': 'medium', 'concern': 'aversion/stress', 'color': '#f59e0b'},
    'embarrassment': {'risk': 'medium', 'concern': 'social anxiety', 'color': '#f59e0b'},
    'excitement': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'fear': {'risk': 'high', 'concern': 'anxiety disorder', 'color': '#ef4444'},
    'gratitude': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'grief': {'risk': 'high', 'concern': 'severe depression', 'color': '#ef4444'},
    'joy': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'love': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'nervousness': {'risk': 'medium', 'concern': 'anxiety', 'color': '#f59e0b'},
    'optimism': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'pride': {'risk': 'low', 'concern': 'positive', 'color': '#10b981'},
    'realization': {'risk': 'low', 'concern': 'insight', 'color': '#10b981'},
    'relief': {'risk': 'low', 'concern': 'stress reduction', 'color': '#10b981'},
    'remorse': {'risk': 'medium', 'concern': 'guilt/regret', 'color': '#f59e0b'},
    'sadness': {'risk': 'high', 'concern': 'depression', 'color': '#ef4444'},
    'surprise': {'risk': 'low', 'concern': 'neutral', 'color': '#6b7280'},
    'neutral': {'risk': 'low', 'concern': 'stable', 'color': '#6b7280'}
}

# Risk Weights
RISK_WEIGHTS = {'high': 3, 'medium': 2, 'low': 1}

# Motivational Quotes
MOTIVATIONAL_QUOTES = [
    "Success is the sum of small efforts repeated day in and day out.",
    "The secret of getting ahead is getting started.",
    "Don't watch the clock; do what it does. Keep going.",
    "The expert in anything was once a beginner.",
    "Focus on being productive instead of busy.",
    "Small progress is still progress.",
    "Your limitation—it's only your imagination.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it."
]

# Statistics Settings
DAILY_GOAL_DEFAULT = 120
WEEKLY_GOAL_DEFAULT = 840
STREAK_GOAL_DEFAULT = 7

# UI Theme
THEME_COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'background': '#f9fafb',
    'card': '#ffffff',
    'text': '#1f2937',
    'text_secondary': '#6b7280'
}