# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🎙️ AUDIO TRANSCRIPTION

**Tool:** `transcribe.py` (custom Python script)
**Location:** `~/.openclaw/workspace/tools/transcribe.py`
**API:** Groq Whisper (whisper-large-v3-turbo)
**Key:** `~/.openclaw/credentials/groq.env`

### Usage

```bash
python3 ~/.openclaw/workspace/tools/transcribe.py <audio_file>
```

### Example

```bash
python3 ~/.openclaw/workspace/tools/transcribe.py ~/.openclaw/media/inbound/file_xxx.ogg
```

### Supported Formats
- .ogg (Telegram voice notes)
- .mp3
- .wav
- .m4a

### Speed
<1 second per minute of audio

### Language
English (en) by default

---

Add whatever helps you do your job. This is your cheat sheet.
