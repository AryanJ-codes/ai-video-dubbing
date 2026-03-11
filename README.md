# 🎙 AI Video Dubbing Pipeline

A fully automated, locally-run Python pipeline + Web UI that takes a YouTube video URL and produces a **Hindi-dubbed version** of the video — complete with AI voice cloning.

---

## ✨ Features

| Stage | Tool Used | What it does |
|---|---|---|
| **Download** | `yt-dlp` | Downloads video from YouTube |
| **Audio Extraction** | `ffmpeg` | Extracts WAV audio track |
| **Transcription** | `OpenAI Whisper` | Converts English speech → timestamped text |
| **Translation** | `deep-translator` | Translates English → Hindi |
| **Voice Cloning TTS** | `Coqui XTTS v2` | Synthesizes Hindi speech cloning the original voice |
| **Video Assembly** | `ffmpeg` | Merges dubbed audio with original video |

---

## 🖥️ Web Interface (Recommended)

Run the pipeline from your browser with a sleek, real-time progress bar:

```bash
source venv/bin/activate
python app.py
```

Then open **[http://localhost:5050](http://localhost:5050)**, paste a YouTube URL and hit **Dub Video**.

The web UI shows:
- 🔵 A glowing animated progress bar
- 📊 Percentage complete + current stage label
- ⏱ Estimated time remaining
- 🎬 In-browser video playback + download when complete

---

## ⚙️ Installation

### 1. System Prerequisites

- **Python 3.9–3.11**
- **FFmpeg** (system install required):
  ```bash
  # macOS
  brew install ffmpeg
  # Ubuntu/Debian
  sudo apt install ffmpeg
  ```

### 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 CLI Usage

```bash
source venv/bin/activate
python main.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

Output video is saved to `outputs/`.

---

## 📁 Project Structure

```
├── app.py               # Flask web server
├── main.py              # CLI entry point & pipeline orchestrator
├── config.py            # Paths and model settings
├── utils.py             # Logging and directory setup
├── downloader.py        # yt-dlp video downloader
├── audio_processing.py  # FFmpeg audio extraction
├── transcription.py     # Whisper transcription
├── translation.py       # English → Hindi translation
├── tts_generation.py    # Coqui XTTS voice cloning + TTS
├── lipsync.py           # Final audio/video merge
├── templates/
│   └── index.html       # Web UI
├── static/
│   └── style.css        # Glassmorphic UI styles
├── videos/              # Downloaded videos
├── audio/               # Extracted / dubbed audio
└── outputs/             # Final dubbed videos
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `ffmpeg: command not found` | Install system ffmpeg (not pip) |
| TTS hangs waiting for input | Run `tts --text "test" --model_name tts_models/multilingual/multi-dataset/xtts_v2` once manually to accept the Coqui TOS |
| Port 5000 Forbidden on macOS | AirPlay uses port 5000 — use `localhost:5050` instead |
| Slow processing | Running on CPU is expected to be slow. GPU recommended for TTS |

---

## 📜 License

This project uses open-source tools. Please ensure you comply with the individual licenses of `Coqui TTS` (CPML), `OpenAI Whisper` (MIT), and `yt-dlp` (Unlicense).
