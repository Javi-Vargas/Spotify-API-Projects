from dotenv import load_dotenv
import os
import requests
from requests import post, get
import base64
import json


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(token_url, headers=headers, data=data)

    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("Sorry, there are no artists with this name. Try again")
        return None
    # else
    return json_result[0]


def get_artists_top_ten_tracks(token, artist_name):
    artist = search_for_artist(token, artist_name)
    artist_id = artist['id']
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


def list_artists_top_ten_tracks(songlist):
    for idx, song in enumerate(songlist):
        print(f"{idx+1}. {song['name']}")


def main():
    token = get_token()
    # result = search_for_artist(token, "Taylor Swift")
    # artist_id = result["id"]

    # songs = get_artists_top_ten_tracks(token, artist_id)  # print 'songs' to get all the meta data on the each song
    songs = get_artists_top_ten_tracks(token, "Cordae")
    list_artists_top_ten_tracks(songs)

    # for idx, song in enumerate(songs):
    #     print(f"{idx+1}. {song['name']}")


if __name__ == '__main__':
    main()
