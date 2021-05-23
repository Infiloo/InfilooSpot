import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import json
from thread import start_new_thread

def show_current_playback():
    global sp
    while True:
        x = sp.current_playback("DE")
        if(any(x)):
            it = x.get("item")
            if(any(it)):
                tit = it["name"]
                if(any(tit)):
                    print(tit)

                    prg = x["progress_ms"]
                    dur = it["duration_ms"]
                    print((prg * 100) / dur)
        sleep(1)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",
                                               client_secret="bb988ada317e44e9a1a73f0b7accf06c",
                                               redirect_uri="http://127.0.0.1:9090",
                                               scope="user-read-playback-state,user-modify-playback-state",
                                               open_browser=False))

# Shows playing devices
res = sp.devices()
pprint(res)

# Change track
sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=['spotify:track:6gdLoMygLsgktydTQ71b15'])

x = sp.current_playback("DE")
print(json.dumps(x, indent=4))
it = x.get("item")
art = it["artists"][0]["name"]
tit = it["name"]
print(art)
print(tit)

start_new_thread(show_current_playback, ())

input("dddd")

