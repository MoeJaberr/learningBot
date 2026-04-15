import os
from datetime import datetime

from core.client import get_client

LECTURES_SUBDIR = "Lectures"


def generate_obsidian_notes(transcript_text: str) -> str | None:
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
                                "Create structured Obsidian notes from this lecture transcript.\n\n"
                                "Rules:\n"
                                "- Use ## and ### headings to group by topic\n"
                                "- Use bullet points for details\n"
                                "- Use [[Term]] wikilinks for key concepts\n"
                                "- Use [[Full Term|Alias]] for aliases where helpful\n"
                                "- Output only the note body (no YAML frontmatter)"
                            ),
                        },
                    ],
                }
            ],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[!] Failed to generate notes: {e}")
        return None


def save_obsidian_note(
    note_text: str,
    filename_prefix: str = "lecture",
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
) -> str:
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", r"C:\Users\moe\Obsidian")
    target_dir = os.path.join(vault_path, LECTURES_SUBDIR)
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(target_dir, f"{filename_prefix}_{timestamp}.md")

    frontmatter = "---\n"
    if aliases:
        frontmatter += "aliases:\n" + "".join(f"  - {a}\n" for a in aliases)
    frontmatter += f"date: {date_str}\nsource: transcript\n"
    if tags:
        frontmatter += "tags: [" + ", ".join(tags) + "]\n"
    frontmatter += "---\n\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter + note_text)

    return file_path
