"""
Theme Management System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class ThemeManager:
    def __init__(self):
        self.current_theme = "default"
        self.themes = {
            "default": config.THEME_COLORS,
            "dark": {
                'primary': '#818cf8',
                'secondary': '#a78bfa',
                'success': '#34d399',
                'warning': '#fbbf24',
                'danger': '#f87171',
                'info': '#60a5fa',
                'background': '#1f2937',
                'card': '#374151',
                'text': '#f9fafb',
                'text_secondary': '#d1d5db'
            },
            "ocean": {
                'primary': '#0ea5e9',
                'secondary': '#06b6d4',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'info': '#3b82f6',
                'background': '#ecfeff',
                'card': '#ffffff',
                'text': '#164e63',
                'text_secondary': '#0e7490'
            }
        }
    
    def get_theme(self, theme_name: str = None):
        """Get theme colors"""
        if theme_name and theme_name in self.themes:
            return self.themes[theme_name]
        return self.themes[self.current_theme]
    
    def set_theme(self, theme_name: str):
        """Set current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_available_themes(self):
        """Get list of available themes"""
        return list(self.themes.keys())
