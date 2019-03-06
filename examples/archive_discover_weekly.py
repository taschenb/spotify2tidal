#!/usr/bin/env python3
import datetime
import logging
from spotify2tidal import Spotify2Tidal

import config

if __name__ == "__main__":
    """Archive the 'Discover Weekly'-playlist from Spotify at Tidal.

    This creates a playlist of the form "Discover Weekly: [YEAR] - [WEEK]".

    In order to work, a Spotify client has to be registered and the
    corresponding ID, secret and redirection URI have to be set in the
    configuration file 'config.py'.
    """
    # Enable logging to see what is going on
    logging.getLogger("spotify2tidal").addHandler(logging.StreamHandler())
    logging.getLogger("spotify2tidal").setLevel(logging.INFO)

    st = Spotify2Tidal(
        config.tidal_username,
        config.tidal_password,
        config.spotify_username,
        config.spotify_client_id,
        config.spotify_client_secret,
        config.spotify_client_redirect_uri,
        config.spotify_discover_weekly_id,
    )

    year, week, day = datetime.datetime.now().isocalendar()
    st.copy_discover_weekly(
        playlist_name=("Discover Weekly: " + str(year) + " - " + str(week))
    )
