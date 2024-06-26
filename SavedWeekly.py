# following the Synsation Tutorial
from dotenv import load_dotenv
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os

client_id = os.getenv("CLIENT_ID_SW")
client_secret = os.getenv("CLIENT_SECRET_SW")
app_secretkey = os.getenv("APP_SECRETKEY")

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = app_secretkey
TOKEN_INFO = 'token_info'


@app.route('/')
def login():  # takes user to login so that we can get the access token needed to make CRUD playlist changes to the a users account
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


@app.route('/redirect')
def redirect_page():
    session.clear()  # clear any existing user data might be in the session
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly', _external=True))


def song_already_in_playlist(saved_weekly_playlist, song_uris):
    # Create a set of song URIs for efficient lookup
    saved_song_uris = {song['track']['uri']
                       for song in saved_weekly_playlist['items']}

    # Check if all song URIs in song_uris are in the saved playlist
    for uri in song_uris:
        if uri not in saved_song_uris:
            return False  # Song not found in playlist

    return True  # All songs found in playlist

# route to save the Discover Weekly songs to a playlist


@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try:
        # get the token info from the session
        token_info = get_token()
    except:
        # if the token info is not found, redirect the user to the login route
        print('User not logged in')
        return redirect("/")

    # sp = spotipy.Spotify(auth=token_info['access_token'])
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # save the user id as a variable to use later for parameters
    user_id = sp.current_user()['id']

    # get all this user's playlists
    current_playlists = sp.current_user_playlists()['items']
    discover_weekly_playlist_id = None
    saved_weekly_playlist_id = None

    # this is me trying to sift through all the playlists and their names
    all_playlists = []  # so this paired the all_playlists.append a few lines below
    songs_added_this_week = []

    # finds the 'discover weekly' and 'saved weekly' playlists and sets the blank variables for them
    for playlist in current_playlists:
        all_playlists.append(playlist['name'])
        if (playlist['name'] == 'Discover Weekly'):
            discover_weekly_playlist_id = playlist['id']
        if (playlist['name'] == 'Saved Weekly'):
            saved_weekly_playlist_id = playlist['id']

    if not saved_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, 'Saved Weekly', True)
        saved_weekly_playlist_id = new_playlist['id']
        print("Had to Create Saved Weekly Playlist")

    if not discover_weekly_playlist_id:
        # return all_playlists
        return 'Discover Weekly not found.'

    # getting the songs from Discover Weekly and adding them to Saved Weekly
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    saved_weekly_playlist = sp.playlist_items(saved_weekly_playlist_id)
    song_uris = []
    # get songs from Discover Weekly
    for song in discover_weekly_playlist['items']:
        song_uri = song['track']['uri']
        song_uris.append(song_uri)
        songs_added_this_week.append(
            song['track']['name'] + ", " + song['track']['artists'][0]['name'])  # put brackets around the statement in the parenthases to have it be more spaced out on the screen
        # songs_added_this_week.append(song['track']['name'])

    # first wanna check that same songs aren't already in there
    if not song_already_in_playlist(saved_weekly_playlist, song_uris):
        sp.user_playlist_add_tracks(
            user_id, saved_weekly_playlist_id, song_uris, None)
        print("OAuth Successful")
        print("This week's songs were added!")
        return (songs_added_this_week)
    else:
        print("OAuth Successful")
        print("Some or all of these songs were already in the playlist.")

    return songs_added_this_week


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(
            token_info['refresh_token'])

    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=url_for('redirect_page', _external=True),
                        scope='user-library-read playlist-modify-public playlist-modify-private')


app.run(debug=True)

# following the Synsation Tutorial
