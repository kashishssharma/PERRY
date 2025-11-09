<<<<<<< HEAD
"""
Statistics and Progress Tracking System
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class StatisticsManager:
    def __init__(self):
        self.stats_file = os.path.join(config.DATA_DIR, "statistics.json")
        self.data = self.load_stats()
    
    def load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'daily_sessions': {},
            'completed_tasks': [],
            'emotion_history': [],
            'total_study_time': 0,
            'longest_streak': 0,
            'current_streak': 0,
            'last_study_date': None,
            'sessions_completed': 0,
            'total_breaks_taken': 0
        }
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def add_session_time(self, seconds: int):
        """Add completed session time"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.data['daily_sessions']:
            self.data['daily_sessions'][today] = 0
        
        self.data['daily_sessions'][today] += seconds
        self.data['total_study_time'] += seconds
        self.data['sessions_completed'] += 1
        
        self._update_streak()
        self.save_stats()
    
    def add_emotion_entry(self, emotion_data: Dict):
        """Add emotion analysis entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'emotions': emotion_data['emotions'],
            'risk_score': emotion_data['risk_score'],
            'primary_emotion': emotion_data['primary_emotion']['emotion'] if emotion_data['primary_emotion'] else None
        }
        
        self.data['emotion_history'].append(entry)
        
        if len(self.data['emotion_history']) > 100:
            self.data['emotion_history'] = self.data['emotion_history'][-100:]
        
        self.save_stats()
    
    def add_completed_task(self, task: str):
        """Add a completed task"""
        entry = {
            'task': task,
            'completed_at': datetime.now().isoformat()
        }
        self.data['completed_tasks'].append(entry)
        self.save_stats()
    
    def get_today_stats(self) -> Dict:
        """Get today's statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_seconds = self.data['daily_sessions'].get(today, 0)
        
        return {
            'study_time_minutes': today_seconds // 60,
            'study_time_formatted': self._format_time(today_seconds),
            'goal_progress': self._calculate_goal_progress(today_seconds, config.DAILY_GOAL_DEFAULT * 60)
        }
    
    def get_week_stats(self) -> Dict:
        """Get this week's statistics"""
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        week_seconds = 0
        daily_breakdown = []
        
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_seconds = self.data['daily_sessions'].get(day_str, 0)
            week_seconds += day_seconds
            
            daily_breakdown.append({
                'day': day.strftime("%A"),
                'date': day_str,
                'minutes': day_seconds // 60,
                'formatted': self._format_time(day_seconds)
            })
        
        return {
            'total_minutes': week_seconds // 60,
            'total_formatted': self._format_time(week_seconds),
            'daily_breakdown': daily_breakdown,
            'goal_progress': self._calculate_goal_progress(week_seconds, config.WEEKLY_GOAL_DEFAULT * 60)
        }
    
    def get_streak_info(self) -> Dict:
        """Get streak information"""
        return {
            'current_streak': self.data['current_streak'],
            'longest_streak': self.data['longest_streak'],
            'goal': config.STREAK_GOAL_DEFAULT,
            'progress': (self.data['current_streak'] / config.STREAK_GOAL_DEFAULT) * 100
        }
    
    def get_emotion_insights(self, days: int = 7) -> Dict:
        """Get emotion insights"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_emotions = [
            e for e in self.data['emotion_history']
            if datetime.fromisoformat(e['timestamp']) > cutoff_date
        ]
        
        if not recent_emotions:
            return {
                'average_risk': 0,
                'most_common_emotion': 'neutral',
                'trend': 'stable',
                'total_entries': 0
            }
        
        avg_risk = sum(e['risk_score'] for e in recent_emotions) / len(recent_emotions)
        
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry['primary_emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        most_common = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
        
        if len(recent_emotions) >= 2:
            first_half_risk = sum(e['risk_score'] for e in recent_emotions[:len(recent_emotions)//2]) / (len(recent_emotions)//2)
            second_half_risk = sum(e['risk_score'] for e in recent_emotions[len(recent_emotions)//2:]) / (len(recent_emotions)//2)
            
            if second_half_risk < first_half_risk - 10:
                trend = 'improving'
            elif second_half_risk > first_half_risk + 10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'average_risk': avg_risk,
            'most_common_emotion': most_common,
            'trend': trend,
            'total_entries': len(recent_emotions)
        }
    
    def _update_streak(self):
        """Update study streak"""
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        if self.data['daily_sessions'].get(today_str, 0) < 600:
            return
        
        last_date_str = self.data.get('last_study_date')
        
        if last_date_str:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                self.data['current_streak'] += 1
            elif days_diff == 0:
                pass
            else:
                self.data['current_streak'] = 1
        else:
            self.data['current_streak'] = 1
        
        if self.data['current_streak'] > self.data['longest_streak']:
            self.data['longest_streak'] = self.data['current_streak']
        
        self.data['last_study_date'] = today_str
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds to readable time"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def _calculate_goal_progress(self, current_seconds: int, goal_seconds: int) -> float:
        """Calculate progress towards goal"""
        if goal_seconds == 0:
            return 100.0
        return min(100.0, (current_seconds / goal_seconds) * 100)
    
    def export_to_csv(self, filename: str = None):
        """Export statistics to CSV"""
        if filename is None:
            filename = os.path.join(config.DATA_DIR, f"study_stats_{datetime.now().strftime('%Y%m%d')}.csv")
        
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Study Time (minutes)', 'Sessions'])
            
            for date, seconds in sorted(self.data['daily_sessions'].items()):
                minutes = seconds // 60
                writer.writerow([date, minutes, ''])
        
        return filename
=======

>>>>>>> 6016f1ed5b98e59f92aab31ec076f93a5d93cd69
