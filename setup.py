import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='spotify2tidal',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        'spotipy >= 2.4.4',
        'tidalapi >= 0.5.0',
        'requests >= 2.11.1'
    ],
    description='Copy Spotify playlists, saved albums/artists/tracks to Tidal',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='taschenb',
    author_email='taschenb@posteo.de',
    license="GPLv3+",
    python_requires='>=3.4',
    url='https://github.com/taschenb/spotify2tidal',
    keywords=['spotify', 'tidal', 'playlist', 'discover weekly'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",],
)
