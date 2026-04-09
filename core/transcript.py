def load_transcript(file_path="output/transcript.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[!] Transcript file not found at: {file_path}")
        return None
