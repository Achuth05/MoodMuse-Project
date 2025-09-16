import os
import requests
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
sb = create_client(SUP_URL, SUP_KEY)

playlists = {
    "Happy / Joyful": [
        "37i9dQZF1DXdPec7aLTmlC",  
        "37i9dQZF1DWVDCf4FD9pC9",  
        "37i9dQZF1DWXb9I5xoXLjp",  
    ],
    "Sad / Melancholic": [
        "37i9dQZF1DX7qK8ma5wgG1",  
        "37i9dQZF1DWY6tYEFs22tT", 
        "37i9dQZF1DX5qyq3XOBAKw", 
        "37i9dQZF1DX3bcfiyW6qms",

    ],
    "Romantic / Love": [
        "37i9dQZF1DWXb9I5xoXLjp",  
        "37i9dQZF1DWXT8uSSn6PRy", 
        "37i9dQZF1DWZl8q7n9GQz1",  
    ],
    "Energetic / Excited": [
        "37i9dQZF1DX76Wlfdnj7AP",  
        "37i9dQZF1DXdxcBWuJkbcy",  
        "37i9dQZF1DX5li09tuOCOl",  
    ],
    "Calm / Relaxed / Chill": [
        "37i9dQZF1DX4WYpdgoIcn6",  
        "37i9dQZF1DWVckOBA0dTYU",  
        "37i9dQZF1DX8vy6e9uJRjo",  
    ],
    "Serious / Thoughtful": [
        "37i9dQZF1DWVrtsSlLKzro",  
        "37i9dQZF1DXbmrSXQ5AIM2",  
    ]
}

def get_spotify_token():
    auth_resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    return auth_resp.json().get("access_token")

token = get_spotify_token()
headers = {"Authorization": f"Bearer {token}"}

def get_audio_features(track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    resp = requests.get(url, headers=headers).json()
    return resp.get("valence"), resp.get("energy"), resp.get("tempo")

def get_all_tracks(playlist_id):
    tracks = []
    limit = 100
    offset = 0
    while True:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
        resp = requests.get(url, headers=headers).json()
        items = resp.get("items", [])
        if not items:
            break
        tracks.extend(items)
        offset += limit
    return tracks


for mood_name, playlist_ids in playlists.items():
    mood = sb.table("moods").select("mood_id").eq("mood_name", mood_name).execute()
    if not mood.data:
        continue
    mood_id = mood.data[0]["mood_id"]

    for playlist_id in playlist_ids:
        tracks = get_all_tracks(playlist_id)
        for t in tracks:
            track = t["track"]
            if not track:
                continue

            spotify_id = track["id"]
            title = track["name"]
            artist = track["artists"][0]["name"]
            release_year = int(track["album"]["release_date"].split("-")[0]) if track["album"]["release_date"] else None

            existing = sb.table("songs").select("spotify_id").eq("spotify_id", spotify_id).execute()
            if existing.data:
                continue

            valence, energy, tempo = get_audio_features(spotify_id)

            sb.table("songs").insert({
                "spotify_id": spotify_id,
                "title": title,
                "artist": artist,
                "release_year": release_year,
                "valence": valence,
                "energy": energy,
                "tempo": tempo,
                "mood_id": mood_id
            }).execute()

        print(f"Inserted {len(tracks)} songs from playlist {playlist_id} into mood {mood_name}")
        time.sleep(0.3)

print("Songs populated!")
