import os
import requests
import time
import random
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")
sb = create_client(SUP_URL, SUP_KEY)

def assign_mood(valence, energy, tempo):
    if valence > 0.7 and energy > 0.7:
        mood_name = "Happy / Joyful"
    elif valence < 0.4 and energy < 0.4:
        mood_name = "Sad / Melancholic"
    elif energy > 0.7 and valence < 0.5:
        mood_name = "Energetic / Excited"
    elif valence > 0.5 and energy < 0.5:
        mood_name = "Romantic / Love"
    else:
        mood_name = "Thoughtful / Calm"

    mood = sb.table("moods").select("mood_id").eq("mood_name", mood_name).execute()
    if mood.data and len(mood.data) > 0:
        return mood.data[0]["mood_id"]
    return None

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

playlist_ids = [
    908622995, 1111146134, 1050834620, 1321842755,
    3155776842, 1234567890
]

for playlist_id in playlist_ids:
    url = f"https://api.deezer.com/playlist/{playlist_id}/tracks"
    while url:
        resp = fetch_url(url)
        if not resp or "data" not in resp:
            break

        for t in resp["data"]:
            deezer_id = str(t["id"])
            title = t["title"]
            artist = t["artist"]["name"]
            release_year = None
            if "album" in t and "release_date" in t["album"]:
                release_year = int(t["album"]["release_date"].split("-")[0])

            # Since Deezer doesn't give these, assign random approximate values
            tempo = random.randint(80, 160)
            valence = round(random.uniform(0.2, 0.9), 2)
            energy = round(random.uniform(0.2, 0.9), 2)

            mood_id = assign_mood(valence, energy, tempo)

            existing = sb.table("songs").select("deezer_id").eq("deezer_id", deezer_id).execute()
            if existing.data:
                continue

            sb.table("songs").insert({
                "deezer_id": deezer_id,
                "title": title,
                "artist": artist,
                "release_year": release_year,
                "tempo": tempo,
                "valence": valence,
                "energy": energy,
                "mood_id": mood_id
            }).execute()

        url = resp.get("next")  # pagination
        time.sleep(0.2)

print("✅ Songs populated from Deezer with generated moods!")



