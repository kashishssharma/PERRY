<<<<<<< HEAD
"""
Pomodoro Timer Management System
"""

import time
from datetime import datetime
from typing import Callable, Optional
import threading

class TimerManager:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.current_phase = 'idle'
        self.remaining_seconds = 0
        self.total_seconds = 0
        self.session_count = 0
        self.completed_sessions = 0
        self.timer_thread = None
        self.start_time = None
        
        self.on_tick_callback = None
        self.on_complete_callback = None
        self.on_phase_change_callback = None
        
    def set_callbacks(self, on_tick=None, on_complete=None, on_phase_change=None):
        """Set callback functions for timer events"""
        self.on_tick_callback = on_tick
        self.on_complete_callback = on_complete
        self.on_phase_change_callback = on_phase_change
    
    def start_focus_session(self, duration_minutes: int):
        """Start a focus session"""
        self.stop()
        self.current_phase = 'focus'
        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.session_count += 1
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        if self.on_phase_change_callback:
            self.on_phase_change_callback('focus', self.session_count)
        
        self._start_countdown()
    
    def start_break(self, duration_minutes: int, break_type: str = 'short'):
        """Start a break session"""
        self.stop()
        self.current_phase = f'{break_type}_break'
        self.total_seconds = duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        if self.on_phase_change_callback:
            self.on_phase_change_callback(self.current_phase, self.session_count)
        
        self._start_countdown()
    
    def pause(self):
        """Pause the current timer"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            return True
        return False
    
    def resume(self):
        """Resume a paused timer"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            return True
        return False
    
    def stop(self):
        """Stop the current timer"""
        self.is_running = False
        self.is_paused = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        return True
    
    def reset(self):
        """Reset all timer data"""
        self.stop()
        self.current_phase = 'idle'
        self.remaining_seconds = 0
        self.total_seconds = 0
        self.session_count = 0
        self.completed_sessions = 0
    
    def _start_countdown(self):
        """Internal method to run countdown"""
        self.timer_thread = threading.Thread(target=self._countdown_loop, daemon=True)
        self.timer_thread.start()
    
    def _countdown_loop(self):
        """Main countdown loop"""
        while self.is_running and self.remaining_seconds > 0:
            if not self.is_paused:
                self.remaining_seconds -= 1
                
                if self.on_tick_callback:
                    self.on_tick_callback(
                        self.remaining_seconds,
                        self.total_seconds,
                        self.current_phase
                    )
                
                time.sleep(1)
            else:
                time.sleep(0.1)
        
        if self.is_running and self.remaining_seconds <= 0:
            self.is_running = False
            
            if self.current_phase == 'focus':
                self.completed_sessions += 1
            
            if self.on_complete_callback:
                self.on_complete_callback(self.current_phase, self.session_count)
    
    def get_formatted_time(self) -> str:
        """Get remaining time formatted as MM:SS"""
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        if self.total_seconds == 0:
            return 0.0
        return ((self.total_seconds - self.remaining_seconds) / self.total_seconds) * 100
    
    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds"""
        return self.total_seconds - self.remaining_seconds
    
    def get_session_info(self) -> dict:
        """Get current session information"""
        return {
            'phase': self.current_phase,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'remaining': self.remaining_seconds,
            'total': self.total_seconds,
            'progress': self.get_progress_percentage(),
            'formatted_time': self.get_formatted_time(),
            'session_count': self.session_count,
            'completed_sessions': self.completed_sessions
        }
=======

>>>>>>> 6016f1ed5b98e59f92aab31ec076f93a5d93cd69
