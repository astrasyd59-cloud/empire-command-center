#!/usr/bin/env python3
"""
Transcribe audio using Groq Whisper API
Usage: python transcribe.py <audio_file>
"""

import os
import sys
import requests
from pathlib import Path

def transcribe_audio(audio_path):
    """Transcribe audio file using Groq Whisper API"""
    
    # Load API key
    env_path = Path.home() / ".openclaw" / "credentials" / "groq.env"
    api_key = None
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('GROQ_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"')
                    break
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in ~/.openclaw/credentials/groq.env")
        sys.exit(1)
    
    audio_file = Path(audio_path)
    if not audio_file.exists():
        print(f"❌ File not found: {audio_path}")
        sys.exit(1)
    
    print(f"🎙️ Transcribing: {audio_file.name}")
    print(f"📏 Size: {audio_file.stat().st_size / 1024:.1f} KB")
    
    # Groq Whisper API endpoint
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Determine file extension
    suffix = audio_file.suffix.lower()
    if suffix == '.ogg':
        file_format = 'ogg'
    elif suffix == '.mp3':
        file_format = 'mp3'
    elif suffix == '.wav':
        file_format = 'wav'
    elif suffix == '.m4a':
        file_format = 'm4a'
    else:
        file_format = 'ogg'  # default
    
    with open(audio_file, 'rb') as f:
        files = {
            'file': (audio_file.name, f, f'audio/{file_format}'),
        }
        data = {
            'model': 'whisper-large-v3-turbo',
            'language': 'en',
            'response_format': 'text'
        }
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            transcription = response.text.strip()
            print(f"\n{'='*60}")
            print("📝 TRANSCRIPTION:")
            print(f"{'='*60}")
            print(transcription)
            print(f"{'='*60}\n")
            
            return transcription
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
        print("Example: python transcribe.py /path/to/audio.ogg")
        sys.exit(1)
    
    transcribe_audio(sys.argv[1])
