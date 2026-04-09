# backend/tutor.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()

def start_socratic_tutor(transcript_path="output/transcript.txt"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[!] OPENAI_API_KEY not found in .env.")
        return

    if not os.path.exists(transcript_path):
        print(f"[!] Transcript not found: {transcript_path}")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    client = openai.OpenAI(api_key=api_key)

    print("\n🧠 Tutoring Mode - Based on the following transcript:")
    print("=" * 60)
    print(transcript[:500] + "...\n")  # Preview only

    question = input("❓ Do you have any questions or topics you struggled with? (or 'no'): ")
    if question.strip().lower() == "no":
        print("✅ No problem! You're done for now.")
        return

    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Socratic tutor helping a student understand lecture material. Ask one guiding question at a time, based on their confusion. Be interactive and student-led."
                    },
                    {
                        "role": "user",
                        "content": f"Here's what I didn't understand: {question}\nContext:\n{transcript[:2000]}"
                    }
                ]
            )
            reply = response.choices[0].message.content
            print("\n💡 Tutor:", reply)
            follow_up = input("\n🗣️ Your reply (or 'exit' to stop): ")
            if follow_up.strip().lower() == "exit":
                print("👋 Session ended.")
                break
            question = follow_up
        except Exception as e:
            print(f"[!] Error during tutoring: {e}")
            break
