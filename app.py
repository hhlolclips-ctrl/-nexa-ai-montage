import streamlit as st
import os, tempfile, requests, cv2, numpy as np, yt_dlp, time, re, random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeAudioClip, 
    concatenate_videoclips, vfx, TextClip, CompositeVideoClip
)
from datetime import datetime
import hashlib

# ==============================
# Page Configuration
# ==============================
st.set_page_config(
    page_title="🔥 NEXA AI Montage Pro v5.0",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# Professional CSS Styling
# ==============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%); min-height: 100vh; }
    .main-title { font-size: 56px; font-weight: 900; background: linear-gradient(135deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; padding: 30px 0 10px; }
    .sub-title { text-align: center; color: #888; font-size: 16px; margin-bottom: 30px; letter-spacing: 2px; }
    .card { background: rgba(255,255,255,0.03); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; padding: 28px; margin: 12px 0; }
    .stButton > button { background: linear-gradient(135deg, #f7971e, #ffd200) !important; color: #000 !important; font-weight: 800 !important; font-size: 20px !important; border-radius: 60px !important; width: 100%; border: none !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🔥 NEXA AI Montage Pro v5.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">AI-Powered Gaming Montage Engine</div>', unsafe_allow_html=True)

# ==============================
# Backend Functions
# ==============================

def download_youtube_video(url):
    output_tmpl = os.path.join(tempfile.gettempdir(), 'yt_input.mp4')
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_tmpl,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_tmpl

def generate_ai_voice(text, api_key, voice_id):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=data, headers=headers, timeout=60)
        if response.status_code == 200:
            path = os.path.join(tempfile.gettempdir(), "ai_voice.mp3")
            with open(path, "wb") as f: f.write(response.content)
            return path
    except: return None

def analyze_gameplay(video_path, max_clips=5):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    timestamps = []
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        if frame_count % int(fps/2) != 0: continue
        # Simple Red Color Detection for "Action"
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        if np.sum(mask == 255) > 6000:
            start = max(0, (frame_count/fps) - 2.5)
            timestamps.append((start, start + 5))
            if len(timestamps) >= max_clips: break
    cap.release()
    return timestamps

# ==============================
# UI Elements
# ==============================
col1, col2 = st.columns(2)
with col1:
    video_url = st.text_input("🔗 YouTube Video URL:")
    api_key = st.text_input("🔑 ElevenLabs API Key:", type="password")
with col2:
    ai_text = st.text_area("✍️ AI Commentary Script:")
    voice_style = st.selectbox("🎭 Voice Style:", ["Action", "Dramatic", "Funny", "Professional"])

# Mapping Voices
voice_map = {"Action": "pNInz6obpgno5Idwkaqm", "Dramatic": "XB0f2Un0U5wYcVhYfKTo", "Funny": "uGZgE7JjHtFw9nUe8WZa", "Professional": "LcfcFyLQk6qF6hTxr8zE"}

if st.button("🚀 Start Rendering Montage"):
    if video_url and api_key and ai_text:
        with st.spinner("Processing..."):
            try:
                vid_path = download_youtube_video(video_url)
                timestamps = analyze_gameplay(vid_path)
                
                base = VideoFileClip(vid_path)
                clips = [base.subclip(s, e).fx(vfx.speedx, 0.8).fadein(0.3).fadeout(0.3) for s, e in timestamps]
                final = concatenate_videoclips(clips, method="compose")
                
                ai_path = generate_ai_voice(ai_text, api_key, voice_map[voice_style])
                if ai_path:
                    ai_audio = AudioFileClip(ai_path)
                    final = final.set_audio(CompositeAudioClip([final.audio.volumex(0.2), ai_audio]))
                
                out_path = os.path.join(tempfile.gettempdir(), "final_nexa.mp4")
                final.write_videofile(out_path, codec="libx264", audio_codec="aac")
                st.success("✅ Montage Complete!")
                st.video(out_path)
            except Exception as e:
                st.error(f"Error: {e}")
