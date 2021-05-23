import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
from sense_hat import SenseHat
import os

HelloShown = False
Exit       = False

# wrap it all in an endless loop to try again if it fails
while Exit == False:
    try:
        sense = SenseHat()
        sense.show_message("...")

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",
                                                       client_secret="bb988ada317e44e9a1a73f0b7accf06c",
                                                       redirect_uri="http://127.0.0.1:9090",
                                                       scope="user-read-playback-state,user-modify-playback-state"))

        # Shows playing devices
        res = sp.devices()
        pprint(res)

        # start UI
        print("Hello at InfilooSpot!")

        ct = [255, 255, 255]
        cb = [100, 100,   0]
        if HelloShown == False:
            HelloShown = True
            sense.show_message("Hello at InfilooSpot!", text_colour=ct, back_colour=cb)
            sense.show_message("_-_-_-_-_-_",           text_colour=ct, back_colour=cb)

        cmd = ' '
        typec = ''
        types = '?'

        while (cmd != 'q') and (cmd != 'e'):
            sense.show_letter(types, text_colour=ct, back_colour=cb)
            cmd = raw_input('Enter track search or cmd n, p, q: ')
            
            if cmd == '1':
                print("all")
                typec = ''
                types = '?'
         
            elif cmd == '2':
                print("artist")
                typec = 'artist'
                types = 'i'

            elif cmd == '3':
                print("album")
                typec = 'album'
                types = 'a'
                
            elif cmd == '4':
                print("track")
                typec = 'track'
                types = 't'       

            elif cmd == '5':
                print("playlist")
                typec = 'playlist'
                types = 'p'       

            elif cmd == 'q':
                print("goodbye")
                sense.show_letter('q', text_colour=ct, back_colour=cb)
                os.system("sudo shutdown now")
                break

            elif cmd == 'e':
                print("exit")
                sense.show_letter('e', text_colour=ct, back_colour=cb)
                Exit = True
                exit()
                break

            elif cmd == 'n':
                print("next")
                sense.show_letter('n', text_colour=ct, back_colour=cb)
                sp.next_track()

            elif cmd == 'p':
                print("previous")
                sense.show_letter('p', text_colour=ct, back_colour=cb)
                sp.previous_track()

            else:
                # only when we have a string to search for
                if cmd != '':
                    # when typec is not empty construct the query
                    if typec != '':
                        cmd = typec + ":" + cmd
                        print(cmd)
                    
                    # search it
                    results = sp.search(q = cmd, limit = 50)

                    # check if there is anything at all
                    if(any(results)):
                        trackURIs = []
                        for idx, track in enumerate(results['tracks']['items']):
                            print(idx, track['name'], track['uri'] )
                            trackURIs.append(track['uri'])
                   
                        sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=trackURIs)
                        
                        sense.show_message(cmd, text_colour=ct, back_colour=cb)

    except:
        if Exit == False:
            print("Ups")


