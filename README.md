# learningBot

A desktop GUI application that functions as an AI-powered learning assistant. Built with a modular frontend/backend/core architecture and integrates with Obsidian for note export.

## Features

- Graphical user interface for interacting with learning content
- Backend processing pipeline with a dedicated core module
- Obsidian note generation from sessions
- Audio transcription support via OpenAI Whisper

## Project Structure

```
learningBot/
├── main.py          # Entry point — launches the GUI
├── frontend/        # UI layer (gui.py)
├── backend/         # Processing and API logic
├── core/            # Shared utilities and models
├── obsidian_notes/  # Generated Obsidian-compatible notes
└── output/          # Session output files
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

## Run

```bash
python main.py
```

## Environment Variables

See `.env.example` for required keys. Never commit your `.env` file.
