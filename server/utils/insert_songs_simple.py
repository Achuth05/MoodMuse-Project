import os
import time
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load .env from server/ directory
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

def getenv_strip(k):
    v = os.getenv(k)
    if v is None:
        return None
    return v.strip().strip('"').strip("'")

SUP_URL = getenv_strip('SUP_URL')
SUP_KEY = getenv_strip('SUP_KEY') or getenv_strip('SUP_SERVICE')
SPOTIFY_CLIENT = getenv_strip('SPOTIFY_CLIENT')
SPOTIFY_SECRET = getenv_strip('SPOTIFY_SECRET')

if not all([SUP_URL, SUP_KEY, SPOTIFY_CLIENT, SPOTIFY_SECRET]):
    raise EnvironmentError('Please set SUP_URL, SUP_KEY (or SUP_SERVICE), SPOTIFY_CLIENT and SPOTIFY_SECRET in server/.env')

sb = create_client(SUP_URL, SUP_KEY)

PLAYLIST_IDS = [
    '37i9dQZF1DXcBWIGoYBM5M',  # Today's Top Hits
    '37i9dQZEVXbMDoHDwVN2tF',  # Global Top 50
    '37i9dQZF1DX0BcQWzuB7ZO',  # Dance/Pop
    '37i9dQZF1DX1lVhptIYRda',  # Rock Classics
]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT, client_secret=SPOTIFY_SECRET))


def fetch_playlist_tracks(playlist_id, limit=None):
    tracks = []
    try:
        # If a per-playlist limit is supplied, respect it
        if limit:
            results = sp.playlist_tracks(playlist_id, limit=limit)
        else:
            results = sp.playlist_tracks(playlist_id, limit=100)
    except spotipy.SpotifyException as e:
        print(f'Failed playlist {playlist_id}: {e}')
        return tracks
    items = results.get('items', [])
    for item in items:
        tr = item.get('track')
        if not tr:
            continue
        sid = tr.get('id')
        if not sid:
            continue
        album = tr.get('album') or {}
        release_year = None
        if album.get('release_date'):
            try:
                release_year = int(album['release_date'].split('-')[0])
            except Exception:
                release_year = None
        tracks.append({'spotify_id': sid, 'title': tr.get('name'), 'artist': ', '.join([a.get('name') for a in tr.get('artists', []) if a.get('name')]), 'release_year': release_year})
    # follow pagination
    next_url = results.get('next')
    # If a limit was provided, do not paginate beyond the initial page
    if limit:
        next_url = None
    while next_url:
        try:
            results = sp.next(results)
        except Exception as e:
            print('Failed to fetch next page:', e)
            break
        items = results.get('items', [])
        for item in items:
            tr = item.get('track')
            if not tr:
                continue
            sid = tr.get('id')
            if not sid:
                continue
            album = tr.get('album') or {}
            release_year = None
            if album.get('release_date'):
                try:
                    release_year = int(album['release_date'].split('-')[0])
                except Exception:
                    release_year = None
            tracks.append({'spotify_id': sid, 'title': tr.get('name'), 'artist': ', '.join([a.get('name') for a in tr.get('artists', []) if a.get('name')]), 'release_year': release_year})
        next_url = results.get('next')
        time.sleep(0.2)
    return tracks


def fetch_audio_features_bulk(ids):
    feats = {}
    for i in range(0, len(ids), 100):
        batch = ids[i:i+100]
        try:
            audio = sp.audio_features(batch)
        except Exception as e:
            print('Audio features fetch failed:', e)
            continue
        for item in audio or []:
            if not item:
                continue
            feats[item.get('id')] = {'valence': item.get('valence'), 'energy': item.get('energy'), 'tempo': item.get('tempo')}
        time.sleep(0.1)
    return feats


def determine_mood(valence, energy, tempo):
    if valence is None or energy is None or tempo is None:
        return 'Serious / Thoughtful'
    if valence >= 0.6 and energy >= 0.6:
        return 'Energetic / Excited'
    if valence >= 0.6 and energy < 0.6:
        return 'Happy / Joyful'
    if valence <= 0.4 and energy <= 0.5:
        return 'Sad / Melancholic'
    if valence >= 0.5 and 0.35 <= energy <= 0.7 and 60 <= tempo <= 110:
        return 'Romantic / Love'
    if valence >= 0.4 and energy < 0.4:
        return 'Calm / Relaxed / Chill'
    return 'Serious / Thoughtful'


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Insert popular Spotify songs into Supabase')
    parser.add_argument('--playlist', '-p', action='append', help='Spotify playlist ID to fetch (repeat for multiple)')
    parser.add_argument('--limit', '-l', type=int, help='Max tracks per playlist (optional)')
    parser.add_argument('--sample', action='store_true', help='Use a small built-in sample of popular track IDs (no playlists)')
    parser.add_argument('--ids', help='Comma-separated list of Spotify track IDs to insert directly')
    parser.add_argument('--file', help='Path to a text file with Spotify track IDs (one per line or comma-separated)')
    args = parser.parse_args()

    print('Fetching playlists...')
    seen = set()
    all_tracks = []
    if args.sample:
        # Small curated sample of well-known track IDs to insert quickly
        sample_ids = [
            '7qiZfU4dY1lWllzX7mPBI3',  # Ed Sheeran - Shape of You
            '0VjIjW4GlUZAMYd2vXMi3b',  # The Weeknd - Blinding Lights
            '3KkXRkHbMCARz0aVfEt68P',  # Jonas Brothers - Sucker (example)
        ]
        print(f'Using sample of {len(sample_ids)} tracks')
        for sid in sample_ids:
            try:
                tr = sp.track(sid)
            except Exception as e:
                print(f'Failed to fetch track {sid}:', e)
                continue
            album = tr.get('album') or {}
            release_year = None
            if album.get('release_date'):
                try:
                    release_year = int(album['release_date'].split('-')[0])
                except Exception:
                    release_year = None
            rec = {'spotify_id': sid, 'title': tr.get('name'), 'artist': ', '.join([a.get('name') for a in tr.get('artists', []) if a.get('name')]), 'release_year': release_year}
            if sid not in seen:
                seen.add(sid)
                all_tracks.append(rec)
    else:
        # ids/file take precedence over playlists if provided
        if args.ids or args.file:
            ids_list = []
            if args.file:
                try:
                    with open(args.file, 'r', encoding='utf-8') as fh:
                        for line in fh:
                            for part in line.strip().split(','):
                                s = part.strip()
                                if s:
                                    ids_list.append(s)
                except Exception as e:
                    print('Failed to read ids file:', e)
            if args.ids:
                ids_list.extend([s.strip() for s in args.ids.split(',') if s.strip()])

            print(f'Fetching metadata for {len(ids_list)} track ids...')
            for sid in ids_list:
                try:
                    tr = sp.track(sid)
                except Exception as e:
                    print(f'Failed to fetch track {sid}:', e)
                    continue
                album = tr.get('album') or {}
                release_year = None
                if album.get('release_date'):
                    try:
                        release_year = int(album['release_date'].split('-')[0])
                    except Exception:
                        release_year = None
                rec = {'spotify_id': sid, 'title': tr.get('name'), 'artist': ', '.join([a.get('name') for a in tr.get('artists', []) if a.get('name')]), 'release_year': release_year}
                if sid not in seen:
                    seen.add(sid)
                    all_tracks.append(rec)
        else:
            playlists_to_use = args.playlist if args.playlist else PLAYLIST_IDS
            for pid in playlists_to_use:
                t = fetch_playlist_tracks(pid, limit=args.limit)
                for tr in t:
                    sid = tr['spotify_id']
                    if sid not in seen:
                        seen.add(sid)
                        all_tracks.append(tr)
    print(f'Collected {len(all_tracks)} unique tracks')

    ids = [t['spotify_id'] for t in all_tracks]
    feats = fetch_audio_features_bulk(ids)

    # Cache mood name -> mood_id from DB
    mood_map = {}
    mood_names = ['Happy / Joyful','Sad / Melancholic','Romantic / Love','Energetic / Excited','Calm / Relaxed / Chill','Serious / Thoughtful']
    for mn in mood_names:
        res = sb.table('moods').select('mood_id').eq('mood_name', mn).execute()
        if res.data and len(res.data) > 0:
            mood_map[mn] = res.data[0]['mood_id']

    inserted = 0
    for tr in all_tracks:
        sid = tr['spotify_id']
        # skip if exists
        try:
            exists = sb.table('songs').select('spotify_id').eq('spotify_id', sid).execute()
            if exists.data:
                continue
        except Exception as e:
            print('DB check failed:', e)
            continue

        f = feats.get(sid, {})
        val = f.get('valence')
        eng = f.get('energy')
        tempo = f.get('tempo')
        mood_name = determine_mood(val, eng, tempo)
        mood_id = mood_map.get(mood_name)

        try:
            sb.table('songs').insert({'spotify_id': sid, 'title': tr.get('title'), 'artist': tr.get('artist'), 'release_year': tr.get('release_year'), 'valence': val, 'energy': eng, 'tempo': tempo, 'mood_id': mood_id}).execute()
            inserted += 1
            if inserted % 50 == 0:
                print(f'Inserted {inserted} songs...')
        except Exception as e:
            print('Insert failed:', e)
        time.sleep(0.02)

    print(f'Done. Inserted {inserted} new songs')


if __name__ == '__main__':
    main()
