from core.client import get_client


def create_tutor_session(transcript_text: str):
    """
    Returns a chat(message: str) -> str callable backed by a running
    conversation. The transcript is cached server-side for the session.
    """
    client = get_client()
    history: list[dict] = []

    system = [
        {
            "type": "text",
            "text": (
                "You are a Socratic tutor helping a student understand lecture material. "
                "Ask one guiding question at a time. "
                "Guide the student toward understanding rather than giving direct answers. "
                "Be concise and encouraging."
            ),
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"Lecture transcript:\n\n{transcript_text[:8000]}",
            "cache_control": {"type": "ephemeral"},
        },
    ]

    def chat(user_message: str) -> str:
        history.append({"role": "user", "content": user_message})
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system,
                messages=history,
            )
            reply = response.content[0].text
            history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"[Tutor error: {e}]"

    return chat
