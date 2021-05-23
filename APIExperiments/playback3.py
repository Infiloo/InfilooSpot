import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
from sense_hat import SenseHat

sense = SenseHat()
sense.show_message("...")

from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials(client_id="680ca5403c694cac9f37b459353cbaeb",
                                        client_secret="bb988ada317e44e9a1a73f0b7accf06c")
sp = spotipy.Spotify(auth_manager=auth_manager)


# Shows playing devices
res = sp.devices()
pprint(res)

# start UI
print("Hello at InfilooSpot!")
sense.show_message("Hello at InfilooSpot!")
cmd = ' '

while cmd != 'q':
    sense.show_letter('?')
    cmd = raw_input('Enter track search or cmd n, p, q: ')
    
    if cmd == 'q':
        print("goodbye")
        sense.show_letter('q')
        break

    elif cmd == 'n':
        print("next")
        sense.show_letter('n')
        sp.next_track()

    elif cmd == 'p':
        print("previous")
        sense.show_letter('p')
        sp.previous_track()

    else:
        results = sp.search(q=cmd, limit=50)

        trackURIs = []
        for idx, track in enumerate(results['tracks']['items']):
            print(idx, track['name'], track['uri'] )
            trackURIs.append(track['uri'])
   
        sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=trackURIs)
        
        sense.show_message(cmd)



