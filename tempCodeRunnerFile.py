    token = get_token()
    result = search_for_artist(token, "Taylor Swift")
    artist_id = result["id"]
    songs = get_songs_by_artists(token, artist_id)
    print(songs)

    for idx, song in enumerate(songs):
        print(f"{idx +1}. {song['name']}")