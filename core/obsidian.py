# core/obsidian.py
import os
from datetime import datetime


def generate_obsidian_notes(transcript_text, openai_client):
    """
    Generates structured, Obsidian-friendly Markdown notes from a lecture transcript.

    Args:
        transcript_text (str): Full transcript.
        openai_client: An OpenAI client instance.

    Returns:
        str: Markdown-formatted notes for Obsidian.
    """
    prompt = f"""
You are an AI assistant helping a student create Markdown notes from a lecture transcript.
The student uses Obsidian and wants the following structure:
- Use markdown headings and subheadings
- Use bullet points where needed
- Use bidirectional links in the form [[Term]]
- Create aliases where appropriate using [[Full Term|Alias]]
- Group content by topic, principle, or concept

TRANSCRIPT:
{transcript_text[:4000]}
"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[!] Failed to generate Obsidian notes: {e}")
        return None

def save_obsidian_note(note_text, base_dir="output/notes", filename_prefix="lecture", aliases=None, tags=None):
    """
    Saves the generated notes to a Markdown file with Obsidian-friendly YAML frontmatter.

    Args:
        note_text (str): Markdown-formatted content.
        base_dir (str): Target directory for saving the note.
        filename_prefix (str): Filename prefix, e.g., 'lecture'.
        aliases (list[str]): Optional list of aliases for the note.
        tags (list[str]): Optional list of tags for the note.

    Returns:
        str: Path to the saved file.
    """
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(base_dir, f"{filename_prefix}_{timestamp}.md")

    yaml_frontmatter = "---\n"
    if aliases:
        yaml_frontmatter += "aliases:\n" + ''.join(f"  - {alias}\n" for alias in aliases)
    yaml_frontmatter += f"date: {date_str}\n"
    yaml_frontmatter += "source: transcript\n"
    if tags:
        yaml_frontmatter += "tags: [" + ', '.join(tags) + "]\n"
    yaml_frontmatter += "---\n\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(yaml_frontmatter + note_text)

    return file_path
