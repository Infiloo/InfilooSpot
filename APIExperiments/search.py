import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="680ca5403c694cac9f37b459353cbaeb",
                                                           client_secret="bb988ada317e44e9a1a73f0b7accf06c"))

results = sp.search(q='Scooter', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])