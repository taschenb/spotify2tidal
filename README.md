# spotify2tidal
spotify2tidal moves playlists, favorite albums and tracks and following artists from a Spotify account to a Tidal account.
It combines [spotipy](https://github.com/plamere/spotipy) and [tidalapi](https://github.com/tamland/python-tidal) to do so.

## Installation

To install, run
```bash
pip install spotify2tidal
```

## Spotify API credentials
Spotify's API requires a registered client with a client ID, client secret and a redirection URI (see [client credential flow](https://developer.spotify.com/documentation/general/guides/authorization-guide/#client-credentials-flow) for more information).
To obtain all three of them, head over to the [Spotify developer dashboard](https://developer.spotify.com/dashboard/) and create a new app. This will generate both ID and secret for you. To use a redirection link in the application, you need to first whitelist it for your client. On the app settings add one to 'Redirect URIs'. If unsure, simply use [https://localhost](https://localhost).

## Spotify 'Discover Weekly' playlist ID
In case you intend to also use your 'Discover Weekly' playlist, you need to obtain the corresponding ID for it. This is necessary because this particular playlist isn't exposed like the rest of you playlist through the API.
To get the ID, simply go to your 'Discover Weekly' playlist, click on the three dots -> Share -> Copy Link. The ID you are looking for is then between "https://open.spotify.com/user/spotify/playlist/" and "?si=".

## Usage
After obtaining all credentials, transferring content is rather simple.

```python
from spotify2tidal import Spotify2Tidal

st = Spotify2Tidal(
	tidal_username="name",
	tidal_password="pwd",
	spotify_client_id="id",
	spotify_client_secret="sec",
	spotify_redirect_uri="uri",
	spotify_discover_weekly_id="weekly",
	)
	
st.copy_discover_weekly()
```
More examples can be found in the examples directory.
