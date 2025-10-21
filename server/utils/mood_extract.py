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
            "great", "good", "amazing", "awesome", "excited", "fun", "positive",
            "blissful", "content", "ecstatic", "elated", "gleeful", "jubilant",
            "merry", "overjoyed", "pleasant", "satisfied", "thrilled", "upbeat",
            "vibrant", "euphoric", "sunny", "jolly", "radiant", "peppy",
            "buoyant", "optimistic", "hopeful", "sparkling", "bright", "lighthearted",
            "cheery", "playful", "grinning", "beaming", "chirpy", "lively",
            "exhilarated", "contented", "fortunate", "blessed", "rejoicing", "joyous",
            "delightful", "festive", "sparkly", "chirping", "thrilled", "tickled",
            "bubbly", "jovial", "effervescent", "gleaming", "smiley"
        ],
        "Sad / Melancholic": [
            "sad", "depressed", "cry", "crying", "tears", "lonely", "down",
            "heartbroken", "gloomy", "upset", "bad", "hurt", "hopeless",
            "miserable", "unhappy", "melancholy", "blue", "sorrowful", "grief",
            "despondent", "forlorn", "wistful", "pensive", "somber", "mourning",
            "dejected", "disheartened", "downcast", "disappointed", "tragic",
            "anguished", "woeful", "lamenting", "glum", "crestfallen", "mournful",
            "dispirited", "heavyhearted", "heartache", "pain", "distressed",
            "desolate", "loneliness", "sadness", "hopelessness", "downhearted",
            "regretful", "bluehearted", "morose", "dreary", "troubled", "aching",
            "grieving", "sullen", "unfortunate", "painful", "tearful", "brokenhearted"
        ],
        "Romantic / Love": [
            "love", "romantic", "heart", "crush", "affection", "caring", "sweet",
            "admire", "couple", "date", "relationship", "beautiful", "cute",
            "adorable", "beloved", "passion", "tender", "intimate", "darling",
            "honey", "sweetheart", "romance", "boyfriend", "girlfriend", "partner",
            "flirt", "flirty", "devoted", "fondness", "enamored", "amour",
            "smitten", "cherish", "kiss", "hug", "hugging", "cuddle", "cuddling",
            "affectionate", "loving", "together", "bond", "relationshipgoals",
            "adore", "sweetie", "bae", "darling", "romantically", "passionate",
            "loveable", "lover", "crushes", "heartfelt", "soulmate", "amorous"
        ],
        "Energetic / Excited": [
            "energetic", "excited", "pumped", "hyped", "ready", "motivated",
            "thrilled", "dynamic", "active", "powerful", "alive", "charged",
            "lively", "spirited", "vivacious", "bubbly", "exhilarated", "enthusiastic",
            "firedup", "vibrant", "eager", "sparked", "amped", "zestful", "alert",
            "peppy", "highspirited", "electrified", "galvanized", "euphoric", "energetically",
            "onfire", "adrenaline", "bursting", "vigorous", "motivating", "readytoroll",
            "fullthrottle", "driven", "exciting", "elated", "upbeat", "hyper", "jubilant"
        ],
        "Calm / Relaxed / Chill": [
            "calm", "relaxed", "peaceful", "chill", "soothing", "gentle", "cozy",
            "comfortable", "tranquil", "easygoing", "rest", "slow",
            "serene", "unwind", "laidback", "composed", "quiet", "soft",
            "mellow", "placid", "content", "balanced", "restful", "light",
            "leisurely", "carefree", "smooth", "hushed", "pacified", "gentlehearted",
            "zen", "meditative", "cool", "harmonious", "relieving", "quietude",
            "blissful", "soothed", "untroubled", "placidly", "peaceably",
            "softspoken", "tranquilized", "serenity", "relaxing", "easygoingly"
        ],
        "Serious / Thoughtful": [
            "serious", "thinking", "thoughtful", "deep", "focus", "reflect",
            "pensive", "philosophical", "quiet", "introspective", "study", "concentrate",
            "contemplative", "meditative", "analytical", "cerebral", "reasoning", "mindful",
            "deliberate", "considerate", "inward", "brooding", "ruminative", "scholarly",
            "reflective", "pondering", "cogitative", "attentive", "examining", "careful",
            "alert", "observant", "thoughtfully", "judicious", "evaluative", "disciplined",
            "serenity", "mindfulthinking", "seriously", "intellectual", "studious",
            "cognitive", "mindset", "insightful", "logical", "focused", "concentration"
        ],
        "Scary / Fearful / Dark": [
            "scared", "fear", "dark", "terrified", "horror", "nervous",
            "afraid", "panic", "creepy", "tense", "ghost", "nightmare",
            "frightened", "alarmed", "dread", "spooked", "anxious", "uneasy",
            "phobic", "haunted", "ominous", "grim", "threatened", "menacing",
            "apprehensive", "shaken", "startled", "shivery", "jumpy", "paranoid",
            "suspenseful", "macabre", "chilling", "bloodcurdling", "gory", "darkness",
            "terrifying", "fearful", "horrifying", "creepycrawlies", "panicstricken",
            "haunting", "spinechilling", "grimdark", "foreboding", "disturbing"
        ],
        "Motivational / Inspirational": [
            "motivate", "motivated", "inspired", "goal", "dream", "success",
            "determined", "focus", "ambition", "dedicated", "driven", "positive", "confidence",
            "encouraged", "empowered", "uplifted", "aspire", "achievement", "courage",
            "resilient", "perseverance", "persistent", "goaloriented", "vision", "hope",
            "optimistic", "energetic", "enthusiastic", "ambitious", "fearless", "strong",
            "hardworking", "dedication", "tenacious", "winning", "overcome", "inspirational",
            "leader", "trailblazer", "motivating", "commitment", "successdriven", "determination",
            "selfbelief", "confident", "proactive", "empower", "uplifting", "focusongoals"
        ]
    }
    # 🔍 Match using substring logic (not exact word)
    for mood, keywords in mood_keywords.items():
        for kw in keywords:
            if re.search(rf"\b{kw}\w*\b", text):  
                return mood

    return None