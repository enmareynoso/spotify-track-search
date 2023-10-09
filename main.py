from dotenv import load_dotenv
import os
load_dotenv()
import base64
import json
from termcolor import colored
import requests
from requests import post

def get_spotify_credentials():
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    return client_id, client_secret

def get_token(client_id, client_secret):
    auth_string = f'{client_id}:{client_secret}'
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {"grant_type": "client_credentials"}

    try:
        result = post(url, headers=headers, data=data)
        result.raise_for_status()  # Raise  exception for HTTP errors
        json_result = result.json()
        token = json_result["access_token"]
        return token
    except requests.exceptions.RequestException as e:
        print(colored(f"Error: {e}", 'red'))
        return None

def search_tracks(query, token):
    search_url = 'https://api.spotify.com/v1/search'
    params = {
        'q': query,
        'type': 'track',
        'limit': 10
    }

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        tracks = data.get('tracks', {}).get('items', [])
        return tracks
    except requests.exceptions.RequestException as e:
        print(colored(f"Error: {e}", 'red'))
        return []

def display_tracks(tracks):
    if not tracks:
        print(colored("No tracks found.", 'yellow'))
        return

    print(colored(f"Found {len(tracks)} tracks:", 'green'))
    for i, track in enumerate(tracks, start=1):
        track_id = track['id']
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        print(colored(f"{i}.", 'blue'), end=' ')
        print(f"{colored(track_name, 'yellow')} by {colored(artists, 'cyan')} (Track ID: {colored(track_id, 'magenta')})")

def main():
    client_id, client_secret = get_spotify_credentials()
    if not client_id or not client_secret:
        print(colored("Client ID and Client Secret not found in environment variables.", 'red'))
        return

    token = get_token(client_id, client_secret)

    if token:
        while True:
            query = input("Enter the song name to search for (or 'exit' to quit): ")

            if query.lower() == 'exit':
                break

            tracks = search_tracks(query, token)
            display_tracks(tracks)
    else:
        print(colored("Failed to retrieve access token.", 'red'))

if __name__ == "__main__":
    main()