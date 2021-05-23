import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import json

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",
                                               client_secret="bb988ada317e44e9a1a73f0b7accf06c",
                                               redirect_uri="http://127.0.0.1:9090",
                                               scope="user-library-read,playlist-read-private"))

"""
results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], "", track['name'])
"""

# request users playlist and show the names
res = sp.current_user_playlists(50, 0)
# pprint(res)
for idx, item in enumerate(res['items']):
    print(idx, item['name'] + " - " + item["id"])

# fetch a single playlist and show the tracks
res = sp.playlist(res["items"][0]["id"])
# print(json.dumps(res["tracks"]["items"][0]["track"]["name"], indent=4))


for idx, item in enumerate(res['tracks']["items"]):
    track = item['track']
    print(idx, track['artists'][0]['name'], " ", track['name'], " ", track["uri"])
