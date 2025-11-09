"""
Audio Management System
"""

import pygame
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.enabled = True
            self.volume = 0.7
        except:
            self.enabled = False
            print("Audio system not available")
    
    def play_start_sound(self):
        """Play session start sound"""
        if not self.enabled:
            return
        
        sound_path = os.path.join(config.SOUNDS_DIR, "start.wav")
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(self.volume)
                sound.play()
            except:
                pass
    
    def play_end_sound(self):
        """Play session end sound"""
        if not self.enabled:
            return
        
        sound_path = os.path.join(config.SOUNDS_DIR, "end.wav")
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(self.volume)
                sound.play()
            except:
                pass
    
    def play_break_sound(self):
        """Play break sound"""
        if not self.enabled:
            return
        
        sound_path = os.path.join(config.SOUNDS_DIR, "break.wav")
        if os.path.exists(sound_path):
            try:
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(self.volume)
                sound.play()
            except:
                pass
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def toggle(self, enabled: bool):
        """Enable or disable audio"""
        self.enabled = enabled