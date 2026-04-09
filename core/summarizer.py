# core/summarizer.py

def summarize_transcript(transcript_text, openai_client):
    """
    Summarizes the given transcript text using OpenAI's chat model.
    
    Args:
        transcript_text (str): The lecture content.
        openai_client: An instance of OpenAI client (e.g., openai.OpenAI(api_key="..."))

    Returns:
        str: The generated summary text.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful academic summarizer for university lectures."},
                {"role": "user", "content": f"Please summarize this lecture:\n\n{transcript_text[:4000]}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[!] Failed to summarize transcript: {e}")
        return None
