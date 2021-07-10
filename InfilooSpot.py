import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import LCD1602
from pynput import keyboard
import os
from thread import start_new_thread
from threading import Thread, Lock
import alsaaudio

# Create Audio Object
mixer       = alsaaudio.Mixer()
mixer.setvolume(100)
currentvol  = mixer.getvolume()
currentvol  = int(currentvol[0])


HelloShown = False          # show some start only when starting for the 1st time and not when we loop
Exit       = False          # we really want to get out

playlists  = []             # the users playlists when fetched after command p
playlistidx = 0             # idx when iterating through th eplaylists

albums     = []             # when we looked for an album this is the list to iterate through
albumidx   = 0              # current selected album

# handle keyboard releae events to see keys immediately without waiting for a Enter
def on_release(key):
    # print('{0} released'.format(key))
    global cmd
    if key == keyboard.Key.enter:
        # Stop listener so we can handle the collect cmd
        return False

    elif key == keyboard.Key.backspace:
        cmd = cmd[:-1]
        printlcd(0, 0, cmd)

    elif key == keyboard.Key.space:
        cmd = cmd + ' '    
        printlcd(0, 0, cmd)

    elif key == keyboard.Key.left:
        cmd = "p"
        return False

    elif key == keyboard.Key.right:
        cmd = "n"
        return False

    elif (key == keyboard.Key.media_volume_up) or (key == keyboard.Key.up):
        cmd = "u"
        return False

    elif (key == keyboard.Key.media_volume_down) or (key == keyboard.Key.down):
        cmd = "d"
        return False
        
    else:
        if hasattr(key, 'char') == True:
            cmd = cmd + str(key.char)    
            printlcd(0, 0, cmd)
            
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
                    # prg = x["progress_ms"]
                    # dur = it["duration_ms"]
                    # print((prg * 100) / dur)

                    printlcd(0, 1, tit)
        sleep(1)

lcd_mutex = Lock()                      # use this mutex to lock the diplay access

# function to write to the display using the mutex to avoid reentrance issues
def printlcd(x, y, str):
    lcd_mutex.acquire()
    LCD1602.write(x, y, (str + "                ")[:16])        # right fill the complete display line but cut everything that is outside of the diasplay
    lcd_mutex.release()

# change the alsa colume up or down by a given % value
def change_volume(volume):
	global currentvol
	if ((currentvol + volume) <= 100) and ((currentvol + volume) >= 0):
	    newVol = currentvol + volume
	    mixer.setvolume(newVol)
	    currentvol = mixer.getvolume()
	    currentvol = int(currentvol[0])
        sp.volume(currentvol)
        print("Volume: " + str(currentvol))


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
                                                       scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"))    # request permissions that we need

        # Shows playing devices
        res = sp.devices()
        pprint(res)
        
        start_new_thread(show_current_playback, ())

        cmd   = ' '
        typec = ''

        while (cmd != 'q') and (cmd != 'e'):
            # Collect key characters until released - which will happen when enter is pressed
            cmd = ''                    #  clear cmd, finally we will find the new cmd here
            with keyboard.Listener(on_release=on_release) as listener:
                listener.join()

            if cmd == '1':
                print("all")
                printlcd(0, 0, "  all")
                typec = ''
                playlists  = []             
                albums     = []
         
            elif cmd == '2':
                print("artist")
                printlcd(0, 0, "  artist")
                typec = 'artist'
                playlists  = []             
                albums     = []

            elif cmd == '3':
                print("album")
                printlcd(0, 0, "  album")
                typec = 'album'
                playlists  = []             
                albums     = []
                
            elif cmd == '4':
                print("track")
                printlcd(0, 0, "  track")
                typec = 'track'
                playlists  = []             
                albums     = []

            elif cmd == '5':
                print("playlist")
                printlcd(0, 0, "  playlist ...")
                albums      = []
                playlists   = sp.current_user_playlists(50, 0)        # fetch playlists from user account
                # playlistidx = 0                                     # keep the idx so we start with the list used at the time selection
                for idx, item in enumerate(playlists['items']):
                    print(idx, item['name'] + " - " + item["id"])
                printlcd(0, 0, "P " + playlists["items"][playlistidx]["name"])

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

            elif cmd == "u":
                print("VolUp")
                change_volume(5)

            elif cmd == "d":
                print("VolDown")
                change_volume(-5)

            elif cmd == 'n':
                print("next")
                if any(playlists):                  # when the list is not empty we are in playlist mode
                    if(len(playlists["items"]) > (playlistidx + 1)):
                        playlistidx += 1
                        printlcd(0, 0, "P " + playlists["items"][playlistidx]["name"])

                elif any(albums):
                   if(len(albums["albums"]["items"]) > (albumidx + 1)):
                        albumidx += 1
                        printlcd(0, 0, "A " + albums["albums"]["items"][albumidx]["name"])    # show album

                else:
                    sp.next_track()

            elif cmd == 'p':
                print("previous")
                if any(playlists):                  # when the list is not empty we are in playlist mode
                    if(playlistidx >= 1):
                        playlistidx -= 1
                        printlcd(0, 0, "P " + playlists["items"][playlistidx]["name"])

                if any(albums):                  # when the list is not empty we are in playlist mode
                    if(albumidx >= 1):
                        albumidx -= 1
                        printlcd(0, 0, "A " + albums["albums"]["items"][albumidx]["name"])    # show album
                       
                else:
                    sp.previous_track()

            elif cmd == '':                         # no input - in playlist mode selection if current playlist
                print("select")
                if any(playlists):                  #  when we have a selected playlist ask spotify to play it
                    sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', playlists["items"][playlistidx]["uri"]) 

                    playlists  = []                 # back to normal mode now playing the playlist
                    # playlistidx = 0               # keep idx so we start from this in the list next time            

                elif any(albums):                   # when we have a selected album ask spotify to play it 
                    sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', albums['albums']["items"][albumidx]["uri"])

                    albums   = []                   # select list to return int normal mode
                    albumidx = 0
                            

            else:
                # only when we have a string to search for
                if cmd != '':
                    # when typec is not empty construct the query
                    if typec != '':
                        cmd = typec + ":" + cmd
                        print(cmd)
                    
                    if(typec != 'album'):
                        # search it if it is just a normal search request for a track
                        results = sp.search(q = cmd, limit = 50)

                        # check if there is anything at all
                        if(any(results)):
                            trackURIs = []
                            for idx, track in enumerate(results['tracks']['items']):
                                print(idx, track['name'], track['uri'] )
                                trackURIs.append(track['uri'])
                    
                            sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=trackURIs)      

                    else:
                        # look for albums and generate a list of found ones to select like a playlist
                        albums   = sp.search(cmd, limit = 50, type = "album")
                        albumidx = 0
                        printlcd(0, 0, "A " + albums["albums"]["items"][albumidx]["name"])    # show 1st album

    except:
        if Exit == False:
            print("Ups")


