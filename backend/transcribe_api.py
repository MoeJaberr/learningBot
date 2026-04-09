# backend/transcribe_api.py

import openai

from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(api_key, input_path, output_path):
    import openai
    import os

    client = openai.OpenAI(api_key=api_key)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"[!] Audio file not found at {input_path}")

    print("[*] Transcribing audio...")

    with open(input_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(response)
    print(f"[✓] Transcript saved to {output_path}")
