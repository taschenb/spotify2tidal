from spotify2tidal.spotify import Spotify
from spotify2tidal.tidal import Tidal


class Spotify2Tidal:
    """Provide a interface for moving from Spotify to Tidal.

    In order to use it, you need a valid Premium-Subscription for Spotify and an
    account at Tidal.
    While Tidal requires just a username and password, Spotify requires some
    work to register a third-party application to access ones account.

    A valid client ID and client secret need to be created and a redirection
    link needs to be whitelisted.
    This can be done in the Spotify developer dashboard by creating a new app.
    This will generate both ID and secret.
    In the app settings, the redirection url can then be whitelisted. If unsure,
    you can use 'http://localhost'.

    To access the 'Discover Weekly' playlist from Spotify, the playlist-ID for
    the 'Discover Weekly' playlists need to be provided. This is necessary
    because this particular playlist is technical not yours, but Spotify's.
    To get the ID, simply go to your 'Discover Weekly' playlist,
    click on the three dots -> Share -> Copy Link. The ID you are looking for is
    then between "https://open.spotify.com/user/spotify/playlist/" and "?si=".

    Parameters
    ----------
    tidal_username: str
        Username for the Tidal-account
    tidal_password: str
        Password for the Tidal-account
    spotify_username: str
        Username for the Spotfiy-account
    spotify_client_id: str
        Client ID, To obtain, see the documentation
    spotify_client_secret: str
        Secret for the client ID. To obtain, see the documentation
    spotify_redirect_uri: str
        URL to redirect after requesting a token, needs whitelisting
    spotify_discover_weekly_id: str, optional
        ID for the users Discover Weekly playlist
    """
    def __init__(
        self,
        tidal_username,
        tidal_password,
        spotify_username,
        spotify_client_id,
        spotify_client_secret,
        spotify_redirect_uri,
        spotify_discover_weekly_id=None,
    ):
        self.spotify = Spotify(
            spotify_username,
            spotify_client_id,
            spotify_client_secret,
            spotify_redirect_uri,
            spotify_discover_weekly_id,
        )
        self.tidal = Tidal(tidal_username, tidal_password)

    def copy_all_spotify_playlists(self):
        """Create all your spotify playlists in tidal."""
        for playlist in self.spotify.own_playlists:
            self._add_spotify_playlist_to_tidal(
                spotify_playlist=playlist, delete_existing=True
            )

    def copy_all_saved_spotify_albums(self):
        """Add all your saved albums to Tidal's favorites."""
        for album in self.spotify.saved_albums:
            artist_name = album["album"]["artists"][0]["name"]
            album_name = album["album"]["name"]

            self.tidal.save_album(album_name, artist_name)

    def copy_all_saved_spotify_artists(self):
        """Add all your saved artists to Tidal's favorites."""
        for artist in self.spotify.saved_artists:
            self.tidal.save_artist(artist["name"])

    def copy_all_saved_spotify_tracks(self):
        """Add all your saved artists to Tidal's favorites."""
        for track in self.spotify.saved_tracks:
            artist_name = track["track"]["artists"][0]["name"]
            track_name = track["track"]["name"]

            self.tidal.save_track(track_name, artist_name)

    def copy_discover_weekly(self, playlist_name="Discover Weekly"):
        """Create a discover weekly in Tidal.

        To save a specific weekly playlist under a different name, use the
        playlist_name to set to something else.

        Parameters
        ----------
        playlist_name: str, optional
            Name of the playlist in Tidal
        """
        self._add_spotify_playlist_to_tidal(
            self.spotify.discover_weekly_playlist,
            playlist_name=playlist_name,
            delete_existing=True,
        )

    def _add_spotify_playlist_to_tidal(
        self, spotify_playlist, playlist_name=None, delete_existing=False
    ):
        """Create a tidal playlist and copy available tracks.

        Parameters
        ----------
        spotify_playlist:
            Playlist to copy to tidal
        playlist_name: string, optional
            Overwrite the playlist name
        delete_existing: bool
            Delete any existing playlist with the same name
        """
        if playlist_name is None:
            playlist_name = spotify_playlist["name"]

        spotify_tracks = self.spotify.tracks_from_playlist(spotify_playlist)

        tidal_playlist_id = self.tidal._create_playlist(
            playlist_name, delete_existing
        )

        for track in spotify_tracks:
            artist = track["track"]["artists"][0]["name"]
            # album = track["track"]["album"]["name"]
            name = track["track"]["name"]
            self.tidal.add_track_to_playlist(
                tidal_playlist_id, artist=artist, name=name
            )
