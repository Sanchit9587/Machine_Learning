import os
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.exceptions
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Spotify Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Genius Credentials
GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")

# Setup Spotify API client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ),
    requests_timeout=120
)

# Create output directory
os.makedirs("lyrics", exist_ok=True)

def get_artist_id(artist_name):
    results = sp.search(q=artist_name, type='artist', limit=1)
    if results is None:
        raise ValueError("Spotify API search returned None. Check your credentials and network connection.")
    artists = results.get('artists', {})
    items = artists.get('items', [])
    if not items:
        raise ValueError(f"No artist found for: {artist_name}")
    return items[0]['id']

def get_all_track_titles(artist_name):
    try:
        artist_id = get_artist_id(artist_name)
        try:
            albums = sp.artist_albums(artist_id, album_type='album', limit=50)
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify error: {e}")
            return []
        except requests.exceptions.ReadTimeout:
            print("Spotify API timed out. Try again or increase the timeout.")
            return []
        track_titles = set()
        for album in albums['items']:
            album_tracks = sp.album_tracks(album['id'])
            for track in album_tracks['items']:
                track_titles.add(track['name'])
        return list(track_titles)
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_lyrics(song_title, artist_name):
    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = f"{base_url}/search"
    params = {"q": f"{song_title} {artist_name}"}

    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        print(f"Failed to search Genius for {song_title}")
        return None
    
    data = response.json()
    hits = data.get("response", {}).get("hits", [])
    for hit in hits:
        if artist_name.lower() in hit["result"]["primary_artist"]["name"].lower():
            song_path = hit["result"]["path"]
            break
    else:
        return None
    print(song_path)
    # Scrape the lyrics from the Genius song page
    song_url = f"https://genius.com{song_path}"
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")

    # Try finding lyrics from all divs that contain them
    lyrics_divs = html.find_all("div", class_=lambda x: bool(x and "Lyrics__Container" in x))
    if not lyrics_divs:
        return None

    lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
    return lyrics.strip()

def save_lyrics(title, lyrics, folder="lyrics"):
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
    filepath = os.path.join(folder, f"{safe_title}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(lyrics)


artist_name = "Pritam"
titles = get_all_track_titles(artist_name)

print(f"Found {len(titles)} tracks.")
# with open("track_names.txt", "w", encoding="utf-8") as f:
#     for title in titles:
#         f.write(f"{title}\n")

for title in titles:
    print(f"Fetching lyrics for: {title}")
    lyrics = get_lyrics(title, artist_name)
    if lyrics:
        save_lyrics(title, lyrics)
        print(f"✅ Saved: {title}")
    else:
        print(f"❌ Lyrics not found for: {title}")

