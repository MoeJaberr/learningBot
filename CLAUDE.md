# learningBot

AI-powered lecture assistant: records audio, transcribes with Whisper, generates Obsidian notes and Anki flashcards, and runs a Socratic tutor — all via a Tkinter GUI.

## Tech Stack

- **Language**: Python 3.11+
- **AI (LLM)**: Anthropic SDK (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`) with prompt caching
- **AI (Transcription)**: OpenAI Whisper API (`whisper-1`) — only remaining OpenAI dependency
- **GUI**: Tkinter (stdlib)
- **Audio**: PyAudio (mic), sounddevice (system/WASAPI loopback)
- **Config**: python-dotenv (`.env` file)
- **Output formats**: Markdown (Obsidian), CSV (Anki)

## Project Structure

```
main.py                   # Entry point — launches frontend/gui.py
core/
  client.py               # Anthropic client singleton (get_client())
  summarizer.py           # Post-session lecture summary
  obsidian.py             # Note generation + save to OBSIDIAN_VAULT_PATH/Lectures/
  tutor.py                # Socratic tutor — create_tutor_session() returns chat fn
  anki.py                 # Flashcard generation + CSV export
  rolling_summary.py      # Real-time incremental summary (Haiku, fired every 2 min)
  recorder.py             # (legacy) audio utilities
  transcript.py           # load_transcript() helper
backend/
  transcribe_api.py       # OpenAI Whisper transcription
  recordMic.py            # Mic recording with on_chunk callback
  record_system_audio.py  # WASAPI loopback system audio recording
  deviceUtils.py          # list_input_devices()
frontend/
  gui.py                  # Main Tkinter UI — rolling summary pane + all buttons
  chatbot.py              # (legacy) CLI chatbot interface
scripts/
  listDevices.py
  testRecord.py
  testTranscribe.py
output/                   # Runtime output: audio.wav, transcript.txt, flashcards_*.csv
```

## Code Style & Conventions

- All new functions must have type hints on parameters and return value
- Core modules receive the Anthropic client via `core.client.get_client()` — never create a new client per call
- Prompt caching: use `"cache_control": {"type": "ephemeral"}` on any block >1024 tokens (transcript, system prompt)
- Thread safety: all GUI updates from background threads must go through `_window.after(0, fn)` — never call Tkinter directly from a thread
- Output files: always write to `output/` directory (auto-created); Obsidian notes go directly to `OBSIDIAN_VAULT_PATH/Lectures/`
- Environment variables loaded via `load_dotenv()` at module init — never hardcode keys

## DO NOT / Known Issues

- **DO NOT** import `openai` outside of `backend/transcribe_api.py` — all LLM work uses Anthropic
- **DO NOT** call Tkinter widget methods directly from background threads — use `window.after(0, fn)` 
- **DO NOT** commit `.env` — it contains `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`
- **DO NOT** record with `duration > 5100` seconds (85 min) — PyAudio buffer limit
- **KNOWN**: System audio recording (WASAPI loopback) requires Windows and a loopback-capable device; will fail silently on macOS/Linux

## Verification Strategy

```bash
# Install dependencies
pip install anthropic openai python-dotenv pyaudio sounddevice

# Verify imports
python -c "from core.client import get_client; from core.anki import generate_flashcards; from frontend.gui import launch_ui; print('OK')"

# Run app
python main.py

# Lint (if ruff installed)
ruff check .
```

## Linters & Formatters

- **Formatter**: `black` (not yet configured — add `pyproject.toml` when ready)
- **Linter**: `ruff` (not yet configured)
- **Type checker**: `mypy` (not yet configured)

To set up:
```bash
pip install black ruff mypy
ruff check .
black .
mypy core/ backend/ frontend/
```
