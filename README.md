# Perry
PERRY addresses a critical challenge faced by students living away from home: the lack of parental guidance, emotional support, and behavioral accountability. Designed specifically for students in high-pressure academic environments (like Kota coaching centers), PERRY acts as a compassionate yet firm "virtual parent."
The Problem

-76% of students report difficulty maintaining study discipline
-84% struggle with excessive social media use during study time
-68% experience emotional isolation when away from family
-Rising mental health crisis among students in competitive academic settings

# The Solution
PERRY provides:

 -AI-powered emotion detection from journal entries (28 emotions)
 -Real-time facial emotion recognition during study sessions
 -Empathetic AI chatbot for 24/7 emotional support
 -Smart focus timer with adaptive website blocking
 -Intelligent schedule management with auto-notifications
 -Comprehensive analytics tracking mental health + productivity

 # Features

-Journal Analyzer: AI-powered emotion detection using RoBERTa
-Talk to Perry: Mental health chatbot with sentiment analysis
-Focus Timer: Pomodoro timer with website blocking
-Schedule Manager: Smart scheduling with auto-notifications
-Emotion Monitoring: Real-time facial emotion recognition
-Analytics: Comprehensive productivity and wellness insights
-Website Blocking: System-level distraction blocking during focus sessions

-Privacy-First Design

-All data stored locally (no cloud uploads)
-Encrypted password storage (SHA-256)
-Camera images analyzed and immediately deleted
-User has full control over monitoring features

 # Administrator Privileges Required
Website blocking requires running as administrator:
bash# Windows (Right-click CMD → "Run as administrator")
streamlit run app2.py

 macOS/Linux
sudo streamlit run app2.py
App works without admin, but website blocking will be disabled.

# Tech Stack
-Core Technologies

Frontend: Streamlit (Python web framework)
Backend: Python 3.8+
Authentication: Custom JWT-like session management

# AI/ML Models

Text Emotion: RoBERTa (Hugging Face Transformers)
Model: emotion_roberta_model (fine-tuned on GoEmotions dataset)
28 emotion labels, 88.3% accuracy
Link : https://drive.google.com/file/d/1fSp69s9e7bu_d4GQOWpCY1l1npwaD2HA/view?usp=sharing

Image Emotion: VGG16-based CNN (TensorFlow/Keras)
Model: model.h5 (7 basic emotions)
OpenCV for face detection (Haar Cascade)
Link : https://drive.google.com/file/d/1JnAL7iX90ek4pi0OrPigsHW4k9RJUGOq/view?usp=sharing

Chatbot: Phi-2 mental health model via Gradio API
Sentiment Analysis: DistilBERT (cardiffnlp/twitter-roberta-base-sentiment)

-System Integration

Website Blocking: System hosts file modification (Windows/macOS/Linux)
Notifications: Windows Toast Notifications (winotify/win10toast)
Activity Logging: CSV-based logging system

-Data Visualization

Plotly (interactive charts)
Pandas + NumPy (data processing)

 Disclaimer
Educational project for personal wellness tracking. For serious mental health concerns, consult qualified healthcare professionals.

# Screenshots:
<img width="1919" height="923" alt="image" src="https://github.com/user-attachments/assets/fc330140-9a7a-442e-9cc2-a4f3bcd977cb" />
<img width="1892" height="909" alt="image" src="https://github.com/user-attachments/assets/9331be4d-b404-4d13-a85a-eda7289a1005" />
<img width="1913" height="909" alt="image" src="https://github.com/user-attachments/assets/3372df56-030b-48a5-8e61-392603983f2e" />
<img width="1598" height="912" alt="image" src="https://github.com/user-attachments/assets/d8be997e-6f28-45fa-882d-8e0e43d848ff" />
<img width="1918" height="914" alt="image" src="https://github.com/user-attachments/assets/f833cea2-56af-49be-ba00-e63a33de251c" />



