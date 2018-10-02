import logging
import requests
import tidalapi


class Tidal:
    """Provide a search-based adding of new favorites to Tidal.

    Add new artists/albums/tracks/albums by searching for them with
    save_artist(), save_album(), and save_track().

    Parameters
    ----------
    username: str
        Tidal username
    password: str
        Tidal password
    """
    def __init__(self, username, password):
        self.tidal_session = self._connect(username, password)

    @property
    def own_playlists(self):
        """All playlists of the current user."""
        return self.tidal_session.get_user_playlists(
            self.tidal_session.user.id
        )

    def add_track_to_playlist(self, playlist_id, name, artist):
        """Search tidal for a track and add it to a playlist.

        Parameters
        ----------
        playlist_id:
            Playlist to add track to
        name: str
            Name of the track
        artist: str
            Artist of the track
        """
        track_id = self._search_track(name, artist)

        if track_id:
            tidal_add_track_url = (
                "https://listen.tidal.com/v1/playlists/"
                + str(playlist_id)
                + "/items"
            )
            r = requests.post(
                tidal_add_track_url,
                headers={
                    "x-tidal-sessionid": self.tidal_session.session_id,
                    "if-none-match": "*",
                },
                data={"trackIds": track_id, "toIndex": 1},
            )
            r.raise_for_status()
            logging.getLogger(__name__).info("Added: %s - %s", artist, name)

        else:
            logging.getLogger(__name__).warning(
                "Could not find track: %s - %s", artist, name
            )

    def delete_existing_playlist(self, playlist_name):
        """Delete any existing playlist with a given name.

        Parameters
        ----------
        playlist_name: str
            Playlist name to delete
        """
        for playlist in self.own_playlists:
            if playlist.name == playlist_name:
                self._delete_playlist(playlist.id)

    def save_album(self, name, artist_name):
        """Find an album and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the album
        artist_name: str
            Name of the artist
        """
        album = self._search_album(name, artist_name)

        if album:
            self.tidal_session.user.favorites.add_album(album)
            logging.getLogger(__name__).warning(
                "Added album: %s from %s", name, artist_name
            )
        else:
            logging.getLogger(__name__).warning(
                "Could not find album: %s from %s", name, artist_name
            )

    def save_artist(self, name):
        """Find an artist by name and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the artist
        """
        artist = self._search_artist(name)

        if artist:
            self.tidal_session.user.favorites.add_artist(artist)
            logging.getLogger(__name__).warning("Added artist: %s", name)
        else:
            logging.getLogger(__name__).warning(
                "Could not find artist: %s", name
            )

    def save_track(self, name, artist_name):
        """Find a track and save it to your favorites.

        Parameters
        ----------
        name: str
            Name of the track
        artist_name: str
            Name of the artist
        """
        track = self._search_track(name, artist_name)

        if track:
            self.tidal_session.user.favorites.add_track(track)
            logging.getLogger(__name__).warning(
                "Added track: %s from %s", name, artist_name
            )
        else:
            logging.getLogger(__name__).warning(
                "Could not find track: %s from %s", name, artist_name
            )

    def _create_playlist(self, playlist_name, delete_existing=False):
        """Create a tidal playlist and return its ID.

        Parameters
        ----------
        playlist_name: str
            Name of the playlist to create
        delete_existing: str
            Delete any existing playlist with the same name
        """
        if delete_existing is True:
            self.delete_existing_playlist(playlist_name)

        tidal_create_playlist_url = (
            "https://listen.tidal.com/v1/users/"
            + str(self.tidal_session.user.id)
            + "/playlists"
        )

        r = requests.post(
            tidal_create_playlist_url,
            data={"title": playlist_name, "description": ""},
            headers={"x-tidal-sessionid": self.tidal_session.session_id},
        )
        r.raise_for_status()

        logging.getLogger(__name__).debug(
            "Created playlist: %s", playlist_name
        )

        return r.json()["uuid"]

    def _connect(self, username, password):
        """Connect to tidal and return a session object.

        Parameters
        ----------
        username: str
            Tidal username
        password: str
            Tidal password
        """
        tidal_session = tidalapi.Session()
        tidal_session.login(username, password)
        return tidal_session

    def _delete_playlist(self, playlist_id):
        """Delete a playlist.

        Parameters
        ----------
        playlist_id: str
            Playlist ID to delete
        """
        playlist_url = "https://listen.tidal.com/v1/playlists/" + playlist_id

        r = requests.delete(
            playlist_url,
            headers={"x-tidal-sessionid": self.tidal_session.session_id},
        )
        r.raise_for_status()

    def _search_track(self, name, artist):
        """Search tidal and return the track ID.

        Parameters
        ----------
        name: str
            Name of the track
        artist: str
            Artist of the track
        """
        tracks = self.tidal_session.search(field="track", value=name).tracks

        for t in tracks:
            if t.artist.name.lower() == artist.lower():
                return t.id

    def _search_album(self, name, artist):
        """Search tidal and return the album ID.

        Parameters
        ----------
        name: str
            Name of the album
        artist: str
            Artist of the album
        """
        albums = self.tidal_session.search(field="album", value=name).albums

        for a in albums:
            if a.artist.name.lower() == artist.lower():
                return a.id

    def _search_artist(self, name):
        """Search tidal and return the artist ID.

        Parameters
        ----------
        name: str
            Name of the artist
        """
        artists = self.tidal_session.search(field="artist", value=name).artists

        for a in artists:
            if a.name.lower() == name.lower():
                return a.id
