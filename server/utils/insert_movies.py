import os
import requests
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")
TMDB_KEY = os.getenv("TMDB_KEY")
sb = create_client(SUP_URL, SUP_KEY)

# Genre → Mood mapping
map = {
    "Comedy": "Happy / Joyful",
    "Drama": "Sad / Melancholic",
    "Romance": "Romantic / Love",
    "Action": "Energetic / Excited",
    "Adventure": "Energetic / Excited",
    "Music": "Happy / Joyful",
    "Documentary": "Serious / Thoughtful",
    "Mystery": "Serious / Thoughtful",
    "Horror": "Scary / Fearful / Dark",
    "Thriller": "Scary / Fearful / Dark",
    "Animation": "Happy / Joyful",
    "Family": "Happy / Joyful",
    "Biography": "Motivational / Inspirational",
    "Sport": "Motivational / Inspirational"
}

genre_resp = requests.get(
    f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_KEY}&language=en-US"
).json()
genre_dict = {g["id"]: g["name"] for g in genre_resp["genres"]}

def fetch_url(url, retries=5, delay=2):
    for _ in range(retries):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print("Request failed, retrying...", e)
            time.sleep(delay)
    return None

languages = ["en", "hi", "ta", "ml", "te", "kn"]

for lang in languages:
    print(f"Fetching movies in language: {lang}")
    for page in range(1, 31): 
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&with_original_language={lang}&page={page}"
        resp = fetch_url(url)
        if not resp:
            print(f"⚠️ Skipping page {page} for language {lang} due to repeated failures")
            continue

        movies = resp.get("results", [])

        for m in movies:
            title = m.get("title")
            release_year = int(m["release_date"].split("-")[0]) if m.get("release_date") else None
            language_code = m.get("original_language")
            api_id = m.get("id")

            existing = sb.table("movies").select("api_id").eq("api_id", api_id).execute()
            if existing.data:
                continue

            genre_name = None
            if m.get("genre_ids"):
                genre_name = genre_dict.get(m["genre_ids"][0])

            mood_id = None
            if genre_name:
                mood_name = map.get(genre_name)
                if mood_name:
                    mood = sb.table("moods").select("mood_id").eq("mood_name", mood_name).execute()
                    if mood.data and len(mood.data) > 0:
                        mood_id = mood.data[0]["mood_id"]

            sb.table("movies").insert({
                "title": title,
                "genre": genre_name,
                "release_year": release_year,
                "language": language_code,
                "mood_id": mood_id,
                "api_id": api_id
            }).execute()

        print(f"✅ Language {lang} - Page {page} inserted successfully")
        time.sleep(0.25)  

print("Movies populated with multiple languages!")

