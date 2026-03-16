# 🔧 TOOLS.md — Groq Whisper

## Groq Whisper API
Purpose: Voice-to-text transcription
Authentication: API key
Credential: GROQ_API_KEY
Model: whisper-large-v3-turbo
Languages: 100+
Status: ✅ AVAILABLE
Speed: <1 second per minute of audio

## Audio Processing
Library: ffmpeg, pydub
Purpose: Format conversion, quality check
Status: ✅ INSTALLED

## Required ENV
GROQ_API_KEY=key
GROQ_MODEL=whisper-large-v3-turbo
GROQ_LANGUAGE=en-US (default)
MAX_AUDIO_SIZE=25MB

## Missing Tools
Real-time streaming, speaker diarization, emotion detection
