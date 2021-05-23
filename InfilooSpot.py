import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import LCD1602
from pynput import keyboard
import os
from thread import start_new_thread
from threading import Thread, Lock

HelloShown = False
Exit       = False

# handle keyboard releae events to see keys immediately without waiting for a Enter
def on_release(key):
    # print('{0} released'.format(key))
    global cmd
    if key == keyboard.Key.enter:
        # Stop listener so we can handle the collect cmd
        return False

    elif key == keyboard.Key.backspace:
        cmd = cmd[:-1]
        printlcd(0, 0, cmd[:16] + "                ")

    elif key == keyboard.Key.space:
        cmd = cmd + ' '    
        printlcd(0, 0, cmd[:16] + "                ")

    elif key == keyboard.Key.left:
        cmd = "p"
        return False

    elif key == keyboard.Key.right:
        cmd = "n"
        return False

    else:
        if hasattr(key, 'char') == True:
            cmd = cmd + str(key.char)    
            printlcd(0, 0, cmd[:16] + "                ")
            
# a background task fetching the current playback and showing it at the 2nd line of the display
def show_current_playback():
    global sp
    while True:
        x = sp.current_playback("DE")
        if((x != None) and (any(x))):
            it = x.get("item")
            if(any(it)):
                tit = it["name"]
                if(any(tit)):
                    # print(tit)
                    prg = x["progress_ms"]
                    dur = it["duration_ms"]
                    # print((prg * 100) / dur)

                    printlcd(0, 1, tit[:16] + "                ")
        sleep(1)

lcd_mutex = Lock()                      # use this mutex to lock the diplay access

# function to write to the display using the mutex to avoid reentrance issues
def printlcd(x, y, str):
    lcd_mutex.acquire()
    LCD1602.write(x, y, str)
    lcd_mutex.release()


# wrap it all in an endless loop to try again if it fails
while Exit == False:
    try:
        # start UI
        LCD1602.init(0x27, 1)
        print("Hello at InfilooSpot!")

        if HelloShown == False:
            HelloShown = True
            printlcd(0, 0, "  InfilooSpot!")
            printlcd(0, 1, "  _-_-_-_-_-_")


        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",            # infiloospot client id
                                                       client_secret="bb988ada317e44e9a1a73f0b7accf06c",        # infiloospot secret
                                                       redirect_uri="http://127.0.0.1:9090",                    # not needed
                                                       scope="user-read-playback-state,user-modify-playback-state"))    # list permissions that we need

        # Shows playing devices
        res = sp.devices()
        pprint(res)
        
        start_new_thread(show_current_playback, ())

        cmd   = ' '
        typec = ''
        types = '?'

        while (cmd != 'q') and (cmd != 'e'):
            # Collect key characters until released - which will happen when enter is pressed
            cmd = ''                    #  clear cmd, finally we will find the new cmd here
            # LCD1602.write(0, 0, "                ")
            with keyboard.Listener(on_release=on_release) as listener:
                listener.join()

            if cmd == '1':
                print("all")
                printlcd(0, 0, "  all               ")
                typec = ''
                types = '?'
         
            elif cmd == '2':
                print("artist")
                printlcd(0, 0, "  artist               ")
                typec = 'artist'
                types = 'i'

            elif cmd == '3':
                print("album")
                printlcd(0, 0, "  album               ")
                typec = 'album'
                types = 'a'
                
            elif cmd == '4':
                print("track")
                printlcd(0, 0, "  track               ")
                typec = 'track'
                types = 't'       

            elif cmd == '5':
                print("playlist")
                printlcd(0, 0, "  playlist               ")
                typec = 'playlist'
                types = 'p'       

            elif cmd == 'q':
                print("goodbye")
                printlcd(0, 0, "  InfilooSpot!  ")
                printlcd(0, 1, "   shutdown     ")

                os.system("sudo shutdown now")
                break

            elif cmd == 'e':
                print("exit")
                printlcd(0, 0, "  InfilooSpot!  ")
                printlcd(0, 1, "      exit      ")

                Exit = True
                exit()
                break

            elif cmd == 'n':
                print("next")
                sp.next_track()

            elif cmd == 'p':
                print("previous")
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

    except:
        if Exit == False:
            print("Ups")


