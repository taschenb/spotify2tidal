from spotify2tidal.spotify import Spotify
from spotify2tidal.tidal import Tidal


class Spotify2tidal:
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
        """Create all your spotify playlists in tidal.
        """
        for playlist in self.spotify.own_playlists:
            self._add_spotify_playlist_to_tidal(
                spotify_playlist=playlist, delete_existing=True
            )

    def copy_all_saved_spotify_albums(self):
        """Add all your saved albums to Tidal's favorites.
        """
        for album in self.spotify.saved_albums:
            artist_name = album["album"]["artists"][0]["name"]
            album_name = album["album"]["name"]

            self.tidal.save_album(album_name, artist_name)

    def copy_all_saved_spotify_artists(self):
        """Add all your saved artists to Tidal's favorites.
        """
        for artist in self.spotify.saved_artists:
            self.tidal.save_artist(artist["name"])

    def copy_all_saved_spotify_tracks(self):
        """Add all your saved artists to Tidal's favorites.
        """
        for track in self.spotify.saved_tracks:
            artist_name = track["track"]["artists"][0]["name"]
            track_name = track["track"]["name"]

            self.tidal.save_track(track_name, artist_name)

    def copy_discover_weekly(self):
        """Create a discover weekly in tidal.
        """
        self._add_spotify_playlist_to_tidal(
            self.spotify.discover_weekly_playlist,
            playlist_name="Discover Weekly",
            delete_existing=True,
        )

    def _add_spotify_playlist_to_tidal(
        self, spotify_playlist, playlist_name=None, delete_existing=False
    ):
        """Create a tidal playlist and copy available tracks.

        Keyword arguments:
        spotify_playlist: Playlist to copy to tidal
        playlist_name: Overwrite the playlist name (optional)
        delete_existing: Delete any existing playlist with the same name
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
