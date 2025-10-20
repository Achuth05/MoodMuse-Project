from flask import Flask, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from supabase import create_client, Client
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

app = Flask(__name__)

# Load .env from the repo's server/ directory (script runs from server/utils)
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

def getenv_strip(k: str) -> Optional[str]:
    v = os.getenv(k)
    if v is None:
        return None
    return v.strip().strip('"').strip("'")

# Configuration - read and strip environment variables
SUP_URL = getenv_strip('SUP_URL')
SUP_SERVICE = getenv_strip('SUP_SERVICE')
SPOTIFY_CLIENT = getenv_strip('SPOTIFY_CLIENT')
SPOTIFY_SECRET = getenv_strip('SPOTIFY_SECRET')

# Validate
missing = [name for name, val in (
    ('SUP_URL', SUP_URL), ('SUP_SERVICE', SUP_SERVICE),
    ('SPOTIFY_CLIENT', SPOTIFY_CLIENT), ('SPOTIFY_SECRET', SPOTIFY_SECRET)
) if not val]
if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}. Please check server/.env")

# Initialize clients
try:
    supabase: Client = create_client(SUP_URL, SUP_SERVICE)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Supabase client: {e}")

try:
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT,
        client_secret=SPOTIFY_SECRET
    ))
except Exception as e:
    raise RuntimeError(f"Failed to initialize Spotify client: {e}")
# Popular playlist IDs to fetch songs from (Spotify curated playlists)
PLAYLIST_IDS = [
    '37i9dQZF1DXcBWIGoYBM5M',  # Today's Top Hits
    '37i9dQZF1DX4sWSpwq3LiO',  # Peaceful Piano
    '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
    '37i9dQZF1DX0XUsuxWHRQd',  # RapCaviar
    '37i9dQZF1DWXRqgorJj26U',  # Rock Classics
]

def determine_mood(valence: float, energy: float) -> int:
    """
    Determine mood_id based on Spotify audio features.
    
    Returns:
        int: mood_id (1-8)
    """
    # 8 - Motivational/Inspirational
    if valence > 0.7 and energy > 0.6:
        return 8
    
    # 1 - Happy/Joyful
    if valence > 0.6 and energy > 0.5:
        return 1
    
    # 4 - Energetic/Excited
    if energy > 0.7:
        return 4
    
    # 7 - Scary/Fearful/Dark
    if valence < 0.3 and energy > 0.6:
        return 7
    
    # 2 - Sad/Melancholic
    if valence < 0.4 and energy < 0.5:
        return 2
    
    # 3 - Romantic/Love
    if valence > 0.5 and energy < 0.6:
        return 3
    
    # 5 - Calm/Relaxed/Chill
    if energy < 0.4 and 0.4 <= valence <= 0.6:
        return 5
    
    # 6 - Serious/Thoughtful
    if 0.4 <= valence <= 0.5 and 0.5 <= energy <= 0.6:
        return 6
    
    # Default to Serious/Thoughtful if no clear match
    return 6

def get_track_details(track_id: str) -> Optional[Dict]:
    """
    Fetch track details and audio features from Spotify.
    
    Args:
        track_id: Spotify track ID
        
    Returns:
        Dict with track information or None if error
    """
    try:
        # Get track metadata
        track = spotify.track(track_id)
        
        # Get audio features
        audio_features = spotify.audio_features([track_id])[0]
        
        if not audio_features:
            return None
        
        # Extract year from release date
        release_date = track['album']['release_date']
        release_year = int(release_date.split('-')[0]) if release_date else None
        
        # Get primary artist
        artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
        
        return {
            'spotify_id': track_id,
            'title': track['name'],
            'artist': artist,
            'release_year': release_year,
            'valence': audio_features['valence'],
            'energy': audio_features['energy'],
            'tempo': audio_features['tempo'],
            'mood_id': determine_mood(audio_features['valence'], audio_features['energy'])
        }
    except Exception as e:
        print(f"Error fetching track {track_id}: {str(e)}")
        return None

def song_exists(spotify_id: str) -> bool:
    """
    Check if a song already exists in the database.
    
    Args:
        spotify_id: Spotify track ID
        
    Returns:
        bool: True if exists, False otherwise
    """
    try:
        response = supabase.table('songs').select('spotify_id').eq('spotify_id', spotify_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking if song exists: {str(e)}")
        return False

def insert_song(song_data: Dict) -> bool:
    """
    Insert a song into the Supabase songs table.
    
    Args:
        song_data: Dictionary containing song information
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if song already exists
        if song_exists(song_data['spotify_id']):
            print(f"Song already exists: {song_data['title']} by {song_data['artist']}")
            return False
        
        supabase.table('songs').insert(song_data).execute()
        print(f"Inserted: {song_data['title']} by {song_data['artist']} (Mood: {song_data['mood_id']})")
        return True
    except Exception as e:
        print(f"Error inserting song: {str(e)}")
        return False

def fetch_and_populate_songs(limit_per_playlist: int = 50) -> Dict:
    """
    Fetch songs from Spotify playlists and populate Supabase.
    
    Args:
        limit_per_playlist: Maximum number of tracks to fetch per playlist
        
    Returns:
        Dict with statistics about the operation
    """
    total_processed = 0
    total_inserted = 0
    total_skipped = 0
    errors = 0
    
    for playlist_id in PLAYLIST_IDS:
        try:
            # Get playlist tracks
            results = spotify.playlist_tracks(playlist_id, limit=limit_per_playlist)
            tracks = results['items']
            
            print(f"\nProcessing playlist: {playlist_id}")
            
            for item in tracks:
                if not item['track'] or not item['track']['id']:
                    continue
                
                track_id = item['track']['id']
                total_processed += 1
                
                # Get track details and audio features
                song_data = get_track_details(track_id)
                
                if song_data:
                    if insert_song(song_data):
                        total_inserted += 1
                    else:
                        total_skipped += 1
                else:
                    errors += 1
                    
        except Exception as e:
            print(f"Error processing playlist {playlist_id}: {str(e)}")
            errors += 1
    
    return {
        'total_processed': total_processed,
        'total_inserted': total_inserted,
        'total_skipped': total_skipped,
        'errors': errors
    }

@app.route('/populate', methods=['POST'])
def populate_songs():
    """
    Endpoint to trigger the song population process.
    """
    try:
        stats = fetch_and_populate_songs()
        return jsonify({
            'success': True,
            'message': 'Song population completed',
            'statistics': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/populate/custom', methods=['POST'])
def populate_custom_playlist():
    """
    Endpoint to populate songs from a custom playlist ID.
    Expects JSON body: {"playlist_id": "spotify_playlist_id", "limit": 50}
    """
    from flask import request
    
    try:
        data = request.get_json()
        playlist_id = data.get('playlist_id')
        limit = data.get('limit', 50)
        
        if not playlist_id:
            return jsonify({
                'success': False,
                'error': 'playlist_id is required'
            }), 400
        
        # Process single playlist
        total_processed = 0
        total_inserted = 0
        total_skipped = 0
        errors = 0
        
        results = spotify.playlist_tracks(playlist_id, limit=limit)
        tracks = results['items']
        
        for item in tracks:
            if not item['track'] or not item['track']['id']:
                continue
            
            track_id = item['track']['id']
            total_processed += 1
            
            song_data = get_track_details(track_id)
            
            if song_data:
                if insert_song(song_data):
                    total_inserted += 1
                else:
                    total_skipped += 1
            else:
                errors += 1
        
        return jsonify({
            'success': True,
            'message': 'Custom playlist processed',
            'statistics': {
                'total_processed': total_processed,
                'total_inserted': total_inserted,
                'total_skipped': total_skipped,
                'errors': errors
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'spotify_connected': True if spotify else False,
        'supabase_connected': True if supabase else False
    }), 200

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Available endpoints:")
    print("  POST /populate - Populate songs from default playlists")
    print("  POST /populate/custom - Populate songs from a custom playlist")
    print("  GET /health - Health check")
    print("\nMake sure to set environment variables:")
    print("  SUP_URL, SUP_SERVICE, SPOTIFY_CLIENT, SPOTIFY_SECRET")
    app.run(debug=True, port=5000)