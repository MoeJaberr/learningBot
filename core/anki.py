import csv
import os
from datetime import datetime

from core.client import get_client


def generate_flashcards(transcript_text: str) -> list[dict] | None:
    """
    Generates Anki-compatible Q&A flashcards from a lecture transcript.
    Returns a list of {"front": ..., "back": ...} dicts.
    """
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": transcript_text,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": (
                                "Generate Anki flashcards from this lecture transcript.\n\n"
                                "Output ONLY raw CSV, two columns: Front,Back\n"
                                "- Front: a clear question or prompt\n"
                                "- Back: a concise answer (1-3 sentences max)\n"
                                "- Aim for 15-25 cards covering the key concepts\n"
                                "- No header row, no markdown fences, no extra text\n"
                                "- Use double quotes around fields containing commas"
                            ),
                        },
                    ],
                }
            ],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if the model includes them
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        cards = []
        for row in csv.reader(lines):
            if len(row) >= 2 and row[0].strip():
                cards.append({"front": row[0].strip(), "back": row[1].strip()})
        return cards
    except Exception as e:
        print(f"[!] Failed to generate flashcards: {e}")
        return None


def save_anki_csv(cards: list[dict], output_dir: str = "output") -> str:
    """Saves flashcards as a CSV importable into Anki (File → Import)."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(output_dir, f"flashcards_{timestamp}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for card in cards:
            writer.writerow([card["front"], card["back"]])
    return path
