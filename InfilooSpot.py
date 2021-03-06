#spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# mpc / mpd
from mpd import MPDClient

# UI
import LCD1602
from pynput import keyboard

#system 
import os
from thread import start_new_thread
from threading import Thread, Lock

#debug and misc
from pprint import pprint
from time import sleep
from enum import Enum

# general operation mode
class GMode(Enum):
    NONE    = 0             # startup - not yet initialized
    SPOT    = 1             # spotify
    IRAD    = 2             # mpd internetradio
    MED     = 3             # mpd media
    EXIT    = 10            # stop all

gmode       = GMode.NONE    # start with blank and wait until the init is done to switch to SPOT 

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

# change general mode
def change_gmode(new_mode):
    global gmode

    print("change mode to: "  + new_mode.name)
    try:
        if(new_mode == GMode.SPOT):
            print("SPOT")
            sp.start_playback()         # go on playing
            mpc.stop();                 # stop playing with mpc
            mpc.clear()

        elif(new_mode == GMode.IRAD):
            print("IRAD")
            sp.pause_playback()         # stop playing spotify
            mpc.stop();                 # stop playing with mpc
            mpc.clear()

        elif(new_mode == GMode.MED):
            print("MED")
            sp.pause_playback()         # stop playing spotify
            mpc.stop();                 # stop playing with mpc
            mpc.clear()

        elif(new_mode == GMode.EXIT):
            print("EXIT")
            sp.pause_playback()         # stop playing spotify
            mpc.stop();                 # stop playing with mpc
            mpc.clear()

    except:
        print("Ups in changemode")
    
    gmode = new_mode

            
# a background task fetching the current playback and showing it at the 2nd line of the display
def show_current_playback():
    global sp
    
    while True:
        try:
            if gmode == GMode.SPOT:
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

            elif (gmode == GMode.IRAD) or (gmode == GMode.MED):
                cursong = mpc.currentsong()
                if(any(cursong)):
                    print(cursong)
                    if("name" in cursong.keys()):
                        # print(cursong["name"])
                        printlcd(0, 1, cursong["name"])
        except:
            print("Ups in show playback")

        sleep(2)


lcd_mutex = Lock()                      # use this mutex to lock the diplay access

# function to write to the display using the mutex to avoid reentrance issues
def printlcd(x, y, str):
    lcd_mutex.acquire()
    LCD1602.write(x, y, (str + "                ")[:16])        # right fill the complete display line but cut everything that is outside of the diasplay
    lcd_mutex.release()

# change the alsa colume up or down by a given % value
def change_volume(volume):
    global currentvol

    try:
        if ((currentvol + volume) <= 100) and ((currentvol + volume) >= 0):
            currentvol = currentvol + volume
            mpc.setvol(currentvol)
            x = sp.current_playback("DE")                       # spotipy crashes when volume() is called but it is not playing yet
            if((x != None) and (any(x))):
                sp.volume(currentvol)
            print("Volume: " + str(currentvol))
    except:
        print("Ups in change_volumer")


# start background thread to show what we are doing
start_new_thread(show_current_playback, ())

# wrap it all in an endless loop to try again if it fails
while Exit == False:
    try:
        if HelloShown == False:
            HelloShown = True

            # start UI
            LCD1602.init(0x27, 1)
            print("Hello at InfilooSpot!")   

            printlcd(0, 0, "  InfilooSpot!")

        # run through init which seems to fail especially when wifi is bad or takes longer to establish
        bInitDone = False
        while bInitDone == False:
            try:
                printlcd(0, 1, "  _-_-_-_-_-_")

                # init and connect to spotify
                sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",            # infiloospot client id
                                                            client_secret="bb988ada317e44e9a1a73f0b7accf06c",        # infiloospot secret
                                                            redirect_uri="http://127.0.0.1:9090",                    # not needed
                                                            scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"))    # request permissions that we need
                # Shows playing spotify connect devices
                res = sp.devices()
                pprint(res)
                printlcd(0, 1, "  _-_-_-_-_-_S")


                # create abd connect mpd client
                mpc = MPDClient()               # create client object
                mpc.timeout = 10                # network timeout in seconds (floats allowed), default: None
                mpc.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
                mpc.connect("localhost", 6600)  # connect to localhost:6600
                print(mpc.mpd_version)          # print the MPD version
                mpc.stop();                     # stop playing with mpc just in case it is running from the last time
                mpc.clear()
                printlcd(0, 1, "  _-_-_-_-_-_SM")

                # set volume back to max
                currentvol = 100
                mpc.setvol(currentvol)
                # sp.volume(currentvol)         # do not set the sp volume as long as we are not playing
                printlcd(0, 1, "  _-_-_-_-_-_SMV")

                bInitDone = True
            except: 
                print("Ups in init")
                sleep(1)
        
        gmode = GMode.SPOT
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
                change_gmode(GMode.SPOT)
                typec = ''
                playlists  = []             
                albums     = []
         
            elif cmd == '2':
                print("artist")
                printlcd(0, 0, "  artist")
                change_gmode(GMode.SPOT)
                typec = 'artist'
                playlists  = []             
                albums     = []

            elif cmd == '3':
                print("album")
                printlcd(0, 0, "  album")
                change_gmode(GMode.SPOT)
                typec = 'album'
                playlists  = []             
                albums     = []
                
            elif cmd == '4':
                print("track")
                printlcd(0, 0, "  track")
                change_gmode(GMode.SPOT)
                typec = 'track'
                playlists  = []             
                albums     = []

            elif cmd == '5':
                print("playlist")
                printlcd(0, 0, "  playlist ...")
                change_gmode(GMode.SPOT)
                albums      = []
                playlists   = sp.current_user_playlists(50, 0)        # fetch playlists from user account
                # playlistidx = 0                                     # keep the idx so we start with the list used at the time selection
                for idx, item in enumerate(playlists['items']):
                    print(idx, item['name'] + " - " + item["id"])
                printlcd(0, 0, "P " + playlists["items"][playlistidx]["name"])

            elif cmd == '6':
                print("I-Radio")
                printlcd(0, 0, " Internet radio")
                change_gmode(GMode.IRAD)
                mpc.load("radiosender")
                mpc.play("1")

            elif cmd == '7':
                print("Media")
                printlcd(0, 0, " Mediaplayer")
                change_gmode(GMode.MED)


            elif cmd == 'q':
                print("goodbye")
                printlcd(0, 0, "  InfilooSpot!  ")
                printlcd(0, 1, "   shutdown     ")
                change_gmode(GMode.EXIT)

                os.system("sudo shutdown now")
                break

            elif cmd == 'e':
                print("exit")
                printlcd(0, 0, "  InfilooSpot!  ")
                printlcd(0, 1, "      exit      ")
                change_gmode(GMode.EXIT)

                # close and disconnect mpc
                mpc.close()                     # send the close command
                mpc.disconnect()                # disconnect from the server

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
                if gmode == GMode.SPOT:
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
                else:
                    try:
                        mpc.next()
                    except:
                        print("Ups next")

            elif cmd == 'p':
                print("previous")
                if gmode == GMode.SPOT:
                    if any(playlists):                  # when the list is not empty we are in playlist mode
                        if(playlistidx >= 1):
                            playlistidx -= 1
                            printlcd(0, 0, "P " + playlists["items"][playlistidx]["name"])

                    elif any(albums):                  # when the list is not empty we are in playlist mode
                        if(albumidx >= 1):
                            albumidx -= 1
                            printlcd(0, 0, "A " + albums["albums"]["items"][albumidx]["name"])    # show album
                        
                    else:
                        sp.previous_track()
                else:
                    try:
                        mpc.previous()
                    except:
                        print("Ups prev")

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


