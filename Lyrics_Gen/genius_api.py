import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load credentials
load_dotenv()

GENIUS_API_TOKEN = os.getenv("GENIUS_API_TOKEN")

# Ensure output directory exists
os.makedirs("lyrics", exist_ok=True)

def get_lyrics(song_title, artist_name):
    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    search_url = f"{base_url}/search"
    params = {"q": f"{song_title} {artist_name}"}

    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
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

    song_url = f"https://genius.com{song_path}"
    page = requests.get(song_url)
    html = BeautifulSoup(page.text, "html.parser")

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

def main():
    artist_name = "Pritam"

    if not os.path.exists("track_names.txt"):
        print("track_names.txt not found. Please run the Spotify fetch script first.")
        return

    with open("track_names.txt", "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    print(f"Found {len(titles)} titles in track_names.txt")

    for title in titles:
        print(f"Fetching lyrics for: {title}")
        lyrics = get_lyrics(title, artist_name)
        if lyrics:
            save_lyrics(title, lyrics)
            print(f"✅ Saved: {title}")
        else:
            print(f"❌ Lyrics not found for: {title}")

if __name__ == "__main__":
    main()
