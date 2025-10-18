import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPEN_AI_KEY"))


pre_moods = [
    "Happy / Joyful",
    "Sad / Melancholic",
    "Romantic / Love",
    "Energetic / Excited",
    "Calm / Relaxed / Chill",
    "Serious / Thoughtful",
    "Scary / Fearful / Dark",
    "Motivational / Inspirational"
]

def extract_mood(user_text: str) -> str:
    prompt = f"""
    The user described their mood as: "{user_text}".
    Choose the single most fitting mood from this list only:
    {", ".join(pre_moods)}.
    Reply with only the mood text, return the exact mood from the list even if there is slash and whitespace, nothing else. 
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0
        )
        mood_name = response.choices[0].message.content.strip()
        if mood_name not in pre_moods:
            return None
        return mood_name
    except Exception as e:
        print("OpenAI error:", e)
        return None

