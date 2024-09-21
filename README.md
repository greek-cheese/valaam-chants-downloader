# Valaam Chants Downloader

## Overview

Valaam Chants Downloader is a Python script designed to scrape, download, and organize chant playlists from the Valaam Monastery's official website. It allows users to select chants and albums, download songs in MP3 format, and automatically add metadata (e.g., song title, album name, artist) to the downloaded files. The project simplifies the process of obtaining and organizing Valaam's freely distributed choir music.

## Features

- Chant Selection: Choose from a variety of chants available on the Valaam Monastery website.
- Album Selection: Select a specific album from the chosen chant for download.
- Playlist Download: Download entire albums or individual songs.
- Metadata Handling: Automatically adds song title, album, artist, and track number to MP3 files using ID3 tags.
- Progress Tracking: Displays download progress for each song.
- Cross-Platform Support: Works on both Windows and Unix-based systems.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/greek-cheese/valaam-chants-downloader.git
    ```

1. Navigate to the project directory:

    ```bash
    cd valaam-chants-downloader
    ```

1. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the script

    ```bash
    python valaam_downloader.py
    ```

1. Folllow the prompts:

- Select a chant.
- Select an album.
- Choose whether to download the entire playlist or individual songs.
- The downloaded MP3 files will be saved in the `downloads` folder, organized by album.

### Example

    ```bash
    $ python valaam_downloader.py
    1. Chant of the Valaam Monastery
    2. Vigil Service
    Please enter your selection number (or 'q' to quit): 1

    1. Album A
    2. Album B
    Please enter your selection number (or 'q' to quit): 2

    Do you want to download the entire playlist? (y/n): y
    Downloading songs: 100%|██████████| 10/10 [00:45<00:00, 4.59s/song]
    ```

## Metadata Handling

This script uses the `mutagen` library to add metadata to the downloaded MP3 files. For each song, the following metadata is set:

- **Title**: The name of the song.
- **Album**: The name of the album.
- **Artist**: The artist or choir responsible for the song.
- **Track Number**: The track's position in the album.

## License

This project is distributed under an open license. Valaam Monastery offers their chants freely, and this project respects their mission by helping users organize and download their music more easily.

## Disclaimer

This project is not affiliated with Valaam Monastery. It simply provides a tool to download and organize freely available music from their website.