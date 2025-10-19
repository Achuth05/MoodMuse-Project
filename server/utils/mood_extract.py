import os
from openai import OpenAI
from difflib import get_close_matches

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

import re

def extract_mood(user_text: str) -> str:
    text = user_text.lower().strip()

    mood_keywords = {
        "Happy / Joyful": [
            "happy", "joy", "joyful", "delighted", "smile", "laugh", "cheerful",
            "great", "good", "amazing", "awesome", "excited", "fun", "positive"
        ],
        "Sad / Melancholic": [
            "sad", "depressed", "cry", "crying", "tears", "lonely", "down",
            "heartbroken", "gloomy", "upset", "bad", "hurt", "hopeless"
        ],
        "Romantic / Love": [
            "love", "romantic", "heart", "crush", "affection", "caring", "sweet",
            "admire", "couple", "date", "relationship", "beautiful", "cute"
        ],
        "Energetic / Excited": [
            "energetic", "excited", "pumped", "hyped", "ready", "motivated",
            "thrilled", "dynamic", "active", "powerful", "alive", "charged"
        ],
        "Calm / Relaxed / Chill": [
            "calm", "relaxed", "peaceful", "chill", "soothing", "gentle", "cozy",
            "comfortable", "tranquil", "easygoing", "rest", "slow"
        ],
        "Serious / Thoughtful": [
            "serious", "thinking", "thoughtful", "deep", "focus", "reflect",
            "pensive", "philosophical", "quiet", "introspective", "study", "concentrate"
        ],
        "Scary / Fearful / Dark": [
            "scared", "fear", "dark", "terrified", "horror", "nervous",
            "afraid", "panic", "creepy", "tense", "ghost", "nightmare"
        ],
        "Motivational / Inspirational": [
            "motivate", "motivated", "inspired", "goal", "dream", "success",
            "determined", "focus", "ambition", "dedicated", "driven", "positive", "confidence"
        ]
    }

    # 🔍 Match using substring logic (not exact word)
    for mood, keywords in mood_keywords.items():
        for kw in keywords:
            if re.search(rf"\b{kw}\w*\b", text):  # Matches cry, crying, cries, etc.
                return mood

    return None
