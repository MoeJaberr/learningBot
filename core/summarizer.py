from core.client import get_client


def summarize_transcript(transcript_text: str) -> str | None:
    client = get_client()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": (
                        "You are a helpful academic summarizer for university lectures. "
                        "Produce a clear, structured summary with key concepts, main points, "
                        "and actionable takeaways."
                    ),
                    "cache_control": {"type": "ephemeral"},
                }
            ],
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
                            "text": "Summarize the lecture transcript above.",
                        },
                    ],
                }
            ],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[!] Failed to summarize: {e}")
        return None
