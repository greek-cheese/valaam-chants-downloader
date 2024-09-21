import urllib.parse as parser
import requests
import json
import re
import os
import mutagen
from tqdm import tqdm
from mutagen.easyid3 import EasyID3

chants_url = r"https://valaam.ru/chants/"
parsed = parser.urlsplit(chants_url)
base_url = f"{parsed.scheme}://{parsed.netloc}"

chant_pattern = (
    r"<a\s+href=\"([^\"]+)\"[^>]*\s+class=\"chants-title[^\"]*\"\s+title=\"([^\"]+)\">"
)
playlist_pattern = r"window\.vmAudioPlayer\((\{.*?\})\);"


def clear_term():
    """
    Clears the terminal screen to improve user experience. 
    Works on both Windows ('cls') and Unix-based systems ('clear').
    """
    os.system("cls" if os.name == "nt" else "clear")


def list_and_select(options: dict) -> set:
    """
    Displays a list of options to the user, allowing them to select an item.
    
    Args:
        options (dict): A dictionary of items to select from, where the key is the option's display name and the value is the corresponding data.
        
    Returns:
        tuple: The selected option's value and key.
    """
    keys = list(options.keys())

    while True:
        for index, key in enumerate(keys):
            print(f"{index}. {key}")

        str_option = input("Please enter your selection number (or 'q'to quit): ")

        if str_option.lower() == "q":
            quit()

        try:
            int_option = int(str_option)
            if 0 <= int_option < len(keys):
                value = options[keys[int_option]] 
                key = keys[int_option]
                return value, key
            else:
                print(f"Please select a number between 0 and {len(keys) - 1}.")
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to quit.")


def get_page(url: str) -> str:
    """
    Fetches the HTML content of a web page.
    
    Args:
        url (str): The URL of the page to fetch.
        
    Returns:
        str: The HTML content of the fetched page.
        
    Raises:
        RuntimeError: If the page fails to load.
    """
    try:
        response = requests.get(url=url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to retrieve the page: {e}")

    html_content = response.content.decode("utf-8")
    return html_content


def get_options(url: str, pattern: str) -> dict:
    """
    Extracts options (e.g., chants or albums) from a web page using a regex pattern.
    
    Args:
        url (str): The URL of the page to scrape.
        pattern (str): The regex pattern used to find the desired data on the page.
        
    Returns:
        dict: A dictionary of extracted options, where the key is the display name and the value is the link.
        
    Raises:
        RuntimeError: If no matches are found.
    """
    html_content = get_page(url=url)
    matches = re.findall(pattern=pattern, string=html_content)
    if matches:
        return {title: href for href, title in matches}
    else:
        raise RuntimeError("No results.")


def get_playlist(url: str, pattern: str) -> list:
    """
    Extracts the playlist data from a web page by searching for a JSON-like block.
    
    Args:
        url (str): The URL of the page to scrape.
        pattern (str): The regex pattern used to find the playlist block.
        
    Returns:
        list: A list of songs found in the playlist.
    """
    html_content = get_page(url=url)
    match = re.search(pattern=pattern, string=html_content, flags=re.DOTALL)

    if match:
        block_of_text = match.group(1)

        try:
            data = json.loads(block_of_text)

            songs = data["songs"]
            return songs

        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
    else:
        print("Block not found")
    return []


def download_mp3(url: str, file_path: str) -> bool:
    """
    Downloads an MP3 file from the given URL and saves it to the specified file path.
    
    Args:
        url (str): The URL of the MP3 file to download.
        file_path (str): The local file path where the MP3 file should be saved.
        
    Returns:
        bool: True if the download is successful, False otherwise.
    """
    if not url.startswith("http"):
        url = f"{base_url}{url}"

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_path}: {e}")
        return False


def add_metadata(file_path: str, album_data, song_data: dict, track_number: int):
    """
    Adds metadata (title, album, artist, track number) to an MP3 file using EasyID3.
    
    Args:
        file_path (str): The local path to the MP3 file.
        album_data (str): The album name to assign to the MP3 file.
        song_data (dict): A dictionary containing the song's metadata (e.g., title, artist).
        track_number (int): The track number to assign to the MP3 file.
    """
    try:
        audio = EasyID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.File(file_path, easy=True)
        audio.add_tags()

    audio['title'] = song_data['name']
    audio['album'] = album_data
    audio['artist'] = song_data['artist']
    audio['tracknumber'] = str(track_number)
    audio.save()


def download_playlist(songs: list, album: str):
    """
    Downloads all songs in a playlist and saves them to a folder named after the album.
    Metadata is added to each MP3 file.
    
    Args:
        songs (list): A list of song data containing URLs and metadata for each song.
        album (str): The album name to assign to the folder and MP3 metadata.
    """
    folder_path = os.path.join("downloads", album)
    os.makedirs(folder_path, exist_ok=True)

    for index, song in enumerate(tqdm(songs, desc="Downloading songs", unit="song"), start=1):
        song_name = song['name']
        song_url = song['url']
        file_path = os.path.join(folder_path, f"{song_name}.mp3")

        if download_mp3(song_url, file_path):
            add_metadata(file_path, album, song, track_number=index)


def main():
    """
    Main script logic:
    1. Retrieves and lists chants for user selection.
    2. Retrieves and lists albums from the selected chant.
    3. Allows user to download either an entire playlist or individual songs.
    4. Downloads selected media and adds metadata.
    """
    chants = get_options(chants_url, chant_pattern)
    clear_term()
    selected_chant, chant = list_and_select(chants)
    clear_term()

    chant_page_url = f"{base_url}{selected_chant}"

    albums = get_options(chant_page_url, chant_pattern)
    selected_album, album = list_and_select(albums)
    clear_term()

    album_url = f"{base_url}{selected_album}"

    playlist = get_playlist(url=album_url, pattern=playlist_pattern)

    download_all = input("Do you want to download the entire playlist? (y/n): ").lower()

    if download_all == 'y':
        download_playlist(playlist, album)
    else:
        song_urls = {song['name']: song['url'] for song in playlist}
        selected_song, song_name = list_and_select(song_urls)

        folder_path = os.path.join("downloads", album)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, f"{song_name}.mp3")

        if download_mp3(selected_song, file_path):
            # Add metadata to the MP3 file
            song_data = next(song for song in playlist if song['name'] == song_name)
            song_index = playlist.index(song_data) + 1  # Get the track number
            add_metadata(file_path, song_data, track_number=song_index)

        print(f"Downloaded and added metadata to {file_path}")

main()
