import requests
import spotipy
import spotipy.util as util
import sys
import tidalapi
import config


def spotify_connect(username, client_id, client_secret, redirect_uri):
    """Connect to spotify and return a session object.

    Use spotify's Authorization Code Flow.
    This requires a registered client at spotify with a valid client-id,
    client-secret and some redirection-url
    More information on authorization:
    https://developer.spotify.com/documentation/general/guides/authorization-guide/
    https://spotipy.readthedocs.io/en/latest/#authorized-requests

    Keyword arguments:
    username: Spotify username
    """
    scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
    token = util.prompt_for_user_token(
        username,
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )

    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Error login into spotify")
        sys.exit()

    return sp


def tidal_connect(username, password):
    """Connect to tidal and return a session object.

    Keyword arguments:
    username: Tidal username
    password: Tidal password
    """
    tidal_session = tidalapi.Session()
    try:
        tidal_session.login(username, password)
    except requests.exceptions.HTTPError:
        print("Error login into tidal")
        sys.exit()
    return tidal_session


def _tidal_delete_existing_playlist(tidal_session, playlist_name):
    """Delete any existing playlist with a given name.

    Keyword arguments:
    tidal_session: Session object of the tidalapi
    playlist_name: Playlist name to delete
    """
    for playlist in tidal_session.get_user_playlists(tidal_session.user.id):
        if playlist.name == playlist_name:
            _tidal_delete_playlist(tidal_session, playlist.id)


def _tidal_delete_playlist(tidal_session, playlist_id):
    """Delete a playlist.

    Keyword arguments:
    tidal_session: Session object of the tidalapi
    playlist_id: Playlist ID to delete
    """
    playlist_url = "https://listen.tidal.com/v1/playlists/" + playlist_id

    r = requests.delete(
        playlist_url, headers={"x-tidal-sessionid": tidal_session.session_id}
    )
    r.raise_for_status()


def tidal_create_all_spotify_playlists(tidal_session, spotify_session):
    """Create all your spotify playlists in tidal.

    Keyword arguments:
    spotify_session: spotipy session object
    tidal_session: Session object of the tidalapi
    """
    result = spotify_session.current_user_playlists()
    own_playlists = result["items"]

    while result["next"]:
        result = spotify_sesion.next(result)
        own_playlists.extend(result["items"])

    for playlist in own_playlists:
        _tidal_add_spotify_playlist(
            tidal_session,
            spotify_session,
            spotify_playlist=playlist,
            delete_existing=True,
        )


def tidal_create_discover_weekly(
    spotify_session, tidal_session, username, discover_weekly_id
):
    """Create a discover weekly in tidal.

    Keyword arguments:
    spotify_session: spotipy session object
    tidal_session: Session object of the tidalapi
    """
    playlist = spotify_session.user_playlist(username, discover_weekly_id)

    _tidal_add_spotify_playlist(
        tidal_session,
        spotify_session,
        playlist,
        playlist_name="Discover Weekly",
        delete_existing=True,
    )


def _tidal_add_spotify_playlist(
    tidal_session,
    spotify_session,
    spotify_playlist,
    playlist_name=None,
    delete_existing=False,
):
    """Create a tidal playlist and copy available tracks.

    Keyword arguments:
    tidal_session: Session object of the tidalapi
    spotify_session: spotipy session object
    spotify_playlist: Playlist id to copy to tidal
    playlist_name: Overwrite the playlist name (optional)
    delete_existing: Delete any existing playlist with the same name
    """
    if playlist_name is None:
        playlist_name = spotify_playlist["name"]

    result = spotify_session.user_playlist(
        user=spotify_playlist["owner"]["id"],
        playlist_id=spotify_playlist["id"],
        fields="tracks,next",
    )["tracks"]

    tracks = result["items"]

    while result["next"]:
        result = spotify_session.next(result)
        tracks.extend(result["items"])

    if delete_existing is True:
        _tidal_delete_existing_playlist(tidal_session, playlist_name)

    tidal_playlist_id = _tidal_create_playlist(tidal_session, playlist_name)
    if not tidal_playlist_id:
        return

    for track in tracks:
        artist = track["track"]["artists"][0]["name"]
        # album = track["track"]["album"]["name"]
        name = track["track"]["name"]
        _tidal_add_track_to_playlist(
            tidal_session, tidal_playlist_id, artist=artist, name=name
        )


def _tidal_add_track_to_playlist(tidal_session, playlist_id, name, artist):
    """Search tidal for a track and add it to a playlist.

    Keyword arguments:
    tidal_session: Session object of the tidalapi
    playlist_id: Playlist to add track to
    name: Name of the track
    artist: Artist of the track
    """
    tidal_track_id = _tidal_search_track(tidal_session, name, artist)

    if tidal_track_id:
        tidal_add_track_url = (
            "https://listen.tidal.com/v1/playlists/"
            + str(playlist_id)
            + "/items"
        )
        r = requests.post(
            tidal_add_track_url,
            headers={
                "x-tidal-sessionid": tidal_session.session_id,
                "if-none-match": "*",
            },
            data={"trackIds": tidal_track_id, "toIndex": 1},
        )
        # r.raise_for_status()

    else:
        print("Could not find on tidal: " + artist + " - " + name)


def _tidal_search_track(tidal_session, name, artist):
    """Search tidal and return the track ID.

    Keyword arguments:
    tidal_session: Session object of the tidalapi
    name: Name of the track
    artist: Artist of the track
    """
    tracks = tidal_session.search(field="track", value=name).tracks

    for t in tracks:
        if t.artist.name.lower() == artist.lower():
            return t.id


def _tidal_create_playlist(tidal_session, playlist_name):
    """Create a tidal playlist and return its ID.

    Keyword arguments:
    playlist_name: Name of the playlist to create
    """
    tidal_create_playlist_url = (
        # "https://listen.tidal.com/v1/users/" + str(tidal_id) + "/playlists"
        "https://listen.tidal.com/v1/users/"
        + str(tidal_session.user.id)
        + "/playlists"
    )

    r = requests.post(
        tidal_create_playlist_url,
        data={"title": playlist_name, "description": ""},
        headers={"x-tidal-sessionid": tidal_session.session_id},
    )
    # r.raise_for_status()

    return r.json()["uuid"]


if __name__ == "__main__":
    tidal_session = tidal_connect(config.tidal_username, config.tidal_password)
    spotify_session = spotify_connect(
        config.spotify_username,
        config.spotify_client_id,
        config.spotify_client_secret,
        config.spotify_client_redirect_uri,
    )

    tidal_create_discover_weekly(
        spotify_session,
        tidal_session,
        config.spotify_username,
        config.spotify_discover_weekly_id,
    )
    tidal_create_all_spotify_playlists(tidal_session, spotify_session)
