from core.client import get_client


def update_rolling_summary(new_segment: str, previous_summary: str = "") -> str:
    """
    Returns an updated rolling summary incorporating new_segment.
    Uses Haiku for speed and cost during real-time recording.
    """
    client = get_client()

    if previous_summary:
        prompt = (
            f"Previous summary:\n{previous_summary}\n\n"
            f"New lecture content:\n{new_segment[-2000:]}\n\n"
            "Update the summary to incorporate the new content. "
            "Keep under 200 words, bullet points grouped by topic."
        )
    else:
        prompt = (
            f"Lecture transcript so far:\n{new_segment[:3000]}\n\n"
            "Summarize what has been covered. "
            "Keep under 200 words, bullet points grouped by topic."
        )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"[Summary error: {e}]"
