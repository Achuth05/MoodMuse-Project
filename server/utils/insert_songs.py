import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT = os.getenv("SPOTIFY_CLIENT")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")

supabase: Client = create_client(SUP_URL, SUP_KEY)

# Mood → Playlist IDs (multi-language)
playlists = {
    "Happy / Joyful": [
        ("English", "37i9dQZF1DXdPec7aLTmlC"),
        ("Hindi", "37i9dQZF1DWXML2TtZaZA6"),
        ("Malayalam", "37i9dQZF1DWTU5gMuwYgOa"),
        ("Tamil", "37i9dQZF1DX7gIoKXt0gmx"),
    ],
    "Sad / Melancholic": [
        ("English", "37i9dQZF1DX7qK8ma5wgG1"),
        ("Hindi", "37i9dQZF1DWXJfnUiYjUKT"),
        ("Malayalam", "37i9dQZF1DWTmu53PG4oHg"),
        ("Tamil", "37i9dQZF1DX4t7T1C8wgVU"),
    ],
    "Romantic / Love": [
        ("English", "37i9dQZF1DXbHcQGb8qq2R"),
        ("Hindi", "37i9dQZF1DX5q67ZpWyRrZ"),
        ("Malayalam", "37i9dQZF1DWTYKFyn3n6AA"),
        ("Tamil", "37i9dQZF1DWVDCf4FD9pC9"),
    ],
    "Energetic / Excited": [
        ("English", "37i9dQZF1DX76Wlfdnj7AP"),
        ("Hindi", "37i9dQZF1DX3PIPIT6lEg5"),
        ("Malayalam", "37i9dQZF1DWT6QQx7aSxUt"),
        ("Tamil", "37i9dQZF1DX9qNZdM354sX"),
    ],
    "Calm / Relaxed / Chill": [
        ("English", "37i9dQZF1DX4WYpdgoIcn6"),
        ("Hindi", "37i9dQZF1DX4Y4VrJZybG3"),
        ("Malayalam", "37i9dQZF1DWTQnBzt7K5G0"),
        ("Tamil", "37i9dQZF1DWYxwmBaMqxsl"),
    ],
    "Serious / Thoughtful": [
        ("English", "37i9dQZF1DWVrtsSlLKzro"),
        ("Hindi", "37i9dQZF1DX7sT9e8nwhSL"),
        ("Malayalam", "37i9dQZF1DX6n88Xxg8u1f"),
        ("Tamil", "37i9dQZF1DX3ZJp8vZeb3A"),
    ]
}

# Map mood name → mood_id (adjust IDs based on your DB)
mood_map = {
    "Happy / Joyful": 1,
    "Sad / Melancholic": 2,
    "Romantic / Love": 3,
    "Energetic / Excited": 4,
    "Calm / Relaxed / Chill": 5,
    "Serious / Thoughtful": 6,
}

# --- Spotify Auth ---
def get_spotify_token():
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT, SPOTIFY_SECRET)
    )
    data = resp.json()
    if "access_token" not in data:
        raise Exception(f"Spotify Auth Failed: {data}")
    return data["access_token"]

# --- Fetch Audio Features (valence, energy, tempo) ---
def fetch_audio_features(track_id, token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return {
        "valence": data.get("valence"),
        "energy": data.get("energy"),
        "tempo": data.get("tempo"),
    }

# --- Fetch Playlist Songs (with pagination) ---

def fetch_playlist_tracks(playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"market": "IN", "limit": 100}
    resp = requests.get(url, params=params).json()
    if "error" in resp:
        print("Error fetching:", resp)
        return []
    return resp.get("items", [])

    all_tracks = []
    data = resp.json()
    if "items" not in data:
        print("Error:", data)

    for item in data["items"]:
        track = item.get("track")
        if track:
            release_year = None
            if "release_date" in track["album"]:
                release_year = track["album"]["release_date"].split("-")[0]
                all_tracks.append({
                    "spotify_id": track["id"],
                    "title": track["name"],
                    "artist": ", ".join([a["name"] for a in track["artists"]]),
                    "release_year": release_year,
                })

    url = data.get("next")  # pagination
    return all_tracks

# --- Insert into Supabase ---
def insert_tracks(mood, language, playlist_id, token):
    tracks = fetch_playlist_tracks(playlist_id)
    print(f"Fetched {len(tracks)} songs from {playlist_id} ({mood} - {language})")

    for song in tracks:
        features = fetch_audio_features(song["spotify_id"], token) or {}
        supabase.table("songs").insert({
            "spotify_id": song["spotify_id"],
            "title": song["title"],
            "artist": song["artist"],
            "release_year": song["release_year"],
            "valence": features.get("valence"),
            "energy": features.get("energy"),
            "tempo": features.get("tempo"),
            "mood_id": mood_map[mood]
        }).execute()

# --- Main ---
if __name__ == "__main__":
    token = get_spotify_token()

    for mood, playlist_list in playlists.items():
        for language, playlist_id in playlist_list:
            insert_tracks(mood, language, playlist_id, token)


