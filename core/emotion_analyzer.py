<<<<<<< HEAD
"""
AI-Powered Emotion Analysis Engine
"""

import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import numpy as np
from typing import List, Dict, Any
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class EmotionAnalyzer:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        self.emotion_labels = list(config.EMOTION_RISK_MAP.keys())
        self.is_loaded = False
        
    def load_model(self):
        """Load or download the emotion detection model"""
        try:
            if os.path.exists(config.MODEL_PATH):
                print("📦 Loading local model...")
                self.tokenizer = RobertaTokenizer.from_pretrained(config.MODEL_PATH)
                self.model = RobertaForSequenceClassification.from_pretrained(config.MODEL_PATH)
            else:
                print("🌐 Downloading model from Hugging Face...")
                print("⏳ This may take 2-3 minutes on first run...")
                self.tokenizer = RobertaTokenizer.from_pretrained(config.EMOTION_MODEL)
                self.model = RobertaForSequenceClassification.from_pretrained(config.EMOTION_MODEL)
                
                os.makedirs(config.MODEL_PATH, exist_ok=True)
                self.tokenizer.save_pretrained(config.MODEL_PATH)
                self.model.save_pretrained(config.MODEL_PATH)
                print("✅ Model saved locally!")
            
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text or text.strip() == "":
            return ""
        return ' '.join(text.split()).strip()
    
    def analyze_emotion(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze emotions in the given text"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        text = self.clean_text(text)
        if not text:
            return None
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        top_probs, top_indices = torch.topk(predictions[0], k=min(top_k, len(self.emotion_labels)))
        
        emotions = []
        for prob, idx in zip(top_probs, top_indices):
            emotion_name = self.emotion_labels[idx.item()]
            emotion_info = config.EMOTION_RISK_MAP.get(emotion_name, {})
            
            emotions.append({
                'emotion': emotion_name,
                'confidence': float(prob.item()),
                'risk_level': emotion_info.get('risk', 'low'),
                'concern': emotion_info.get('concern', 'unknown'),
                'color': emotion_info.get('color', '#6b7280')
            })
        
        risk_score = self.calculate_risk_score(emotions)
        recommendation = self.generate_recommendation(risk_score, emotions)
        
        return {
            'emotions': emotions,
            'risk_score': risk_score,
            'recommendation': recommendation,
            'primary_emotion': emotions[0] if emotions else None
        }
    
    def calculate_risk_score(self, emotions: List[Dict]) -> float:
        """Calculate overall mental health risk score (0-100)"""
        if not emotions:
            return 0.0
        
        total_score = sum(
            config.RISK_WEIGHTS[e['risk_level']] * e['confidence'] 
            for e in emotions
        )
        max_score = sum(
            config.RISK_WEIGHTS['high'] * e['confidence'] 
            for e in emotions
        )
        
        if max_score == 0:
            return 0.0
        
        return (total_score / max_score) * 100
    
    def generate_recommendation(self, risk_score: float, emotions: List[Dict]) -> str:
        """Generate personalized recommendation"""
        if risk_score > 66:
            return """⚠️ **HIGH STRESS DETECTED**

Your emotional state suggests significant stress. Consider:
- Taking a longer break (15-30 minutes)
- Practice deep breathing or meditation
- Talk to someone you trust
- Consider professional support if feelings persist
- Reduce study session length temporarily"""
        elif risk_score > 40:
            return """⚡ **MODERATE STRESS**

You're experiencing some stress. Try:
- Take a 5-10 minute break
- Do some light stretching or walking
- Listen to calming music
- Break tasks into smaller chunks
- Practice mindfulness techniques"""
        elif risk_score > 20:
            return """✅ **BALANCED STATE**

Your emotions are relatively balanced. Keep:
- Maintaining regular breaks
- Staying hydrated
- Practicing good study habits
- Being kind to yourself"""
        else:
            return """🌟 **EXCELLENT STATE**

You're in a great emotional state! Keep:
- Your positive mindset
- Current study routine
- Regular self-care practices
- Celebrating small wins"""
    
    def get_adaptive_session_adjustment(self, risk_score: float, current_duration: int) -> int:
        """Suggest session duration adjustment based on emotional state"""
        if risk_score > 66:
            return max(15, int(current_duration * 0.6))
        elif risk_score > 40:
            return max(15, int(current_duration * 0.8))
        elif risk_score < 20:
            return min(60, int(current_duration * 1.2))
        else:
            return current_duration
=======

>>>>>>> 6016f1ed5b98e59f92aab31ec076f93a5d93cd69
