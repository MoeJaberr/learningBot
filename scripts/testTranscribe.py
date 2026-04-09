import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.transcribe_api import transcribe_audio

API_KEY = os.environ.get("OPENAI_API_KEY", "")

transcribe_audio(api_key=API_KEY)
