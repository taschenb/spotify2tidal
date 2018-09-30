import spotipy
import spotipy.util as util


class Spotify:
    def __init__(
        self,
        username,
        client_id,
        client_secret,
        client_redirect_uri,
        discover_weekly_id=None,
    ):
        self.spotify_session = self._connect(
            username, client_id, client_secret, client_redirect_uri
        )
        self.username = username
        self._discover_weekly_id = discover_weekly_id

    @property
    def own_playlists(self):
        result = self.spotify_session.current_user_playlists()
        playlists = result["items"]

        while result["next"]:
            result = self.spotify_sesion.next(result)
            playlists.extend(result["items"])

        return playlists

    @property
    def discover_weekly_playlist(self):
        if self._discover_weekly_id:
            return self.spotify_session.user_playlist(
                self.username, self._discover_weekly_id
            )
        else:
            raise ValueError("No discover weekly ID set")

    def tracks_from_playlist(self, playlist):
        result = self.spotify_session.user_playlist(
            user=playlist["owner"]["id"],
            playlist_id=playlist["id"],
            fields="tracks,next",
        )["tracks"]

        tracks = result["items"]

        while result["next"]:
            result = self.spotify_session.next(result)
            tracks.extend(result["items"])

        return tracks

    def _connect(
        self, username, client_id, client_secret, client_redirect_uri
    ):
        """Connect to Spotify and return a session object.

        Use spotify's Authorization Code Flow.
        This requires a registered client at spotify with a valid client-id,
        client-secret and some redirection-url
        More information on authorization:
        https://developer.spotify.com/documentation/general/guides/authorization-guide/
        https://spotipy.readthedocs.io/en/latest/#authorized-requests

        Keyword arguments:
        username: Spotify username
        client_id: Spotify client ID (see links above how to obtain)
        client_secret: Spotify client secret (see links above how to obtain)
        redirect_uri: Spotify client redirection (see links above how to obtain)
        """
        scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
        token = util.prompt_for_user_token(
            username,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=client_redirect_uri,
        )

        if not token:
            raise ValueError("Could not connect to Spotify")

        return spotipy.Spotify(auth=token)
