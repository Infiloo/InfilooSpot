#spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from pprint import pprint
from time import sleep

import os
from _thread import start_new_thread
from threading import Thread, Lock

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

###  global status data
Volume = 100


''' combo_Type select serarch type - when Playlists are selected fetch them from spotify and fill combobox'''
def cbType_Select(event):
    if(cbType.get() == "Playlists"):
        # Playlists is selcted      
        cbSearch['state'] = 'readonly'                          # block edit
        playlists   = sp.current_user_playlists(50, 0)          # fetch playlists from user account

        list = []
        cbSearch['values'] = playlists
        for idx, item in enumerate(playlists['items']):
            #     print(idx, item['name'] + " - " + item["id"])
           list.append(item['name'])
        cbSearch['values'] = list       
        cbSearch.event_generate('<Button-1>')     
    else:
        # something we need t e´search is selected - list list
        cbSearch['values']={}             # clear list if combobox again
        cbSearch.set("")
        cbSearch['state'] = 'normal'      # enable edit



''' trResult_Select Item selected - use the colum to decide what to do'''
def trResult_Select(event):
    real_coords = (trResult.winfo_pointerx() - trResult.winfo_rootx(),
                   trResult.winfo_pointery() - trResult.winfo_rooty())
    item = trResult.identify('item', *real_coords)

    for selected_item in trResult.selection():
        item = trResult.item(selected_item)
        tags = item['tags']
        col  = trResult.identify_column(real_coords[0])
        if(col == "#1"):
            icol = 0
            type = "track:"
        if(col == "#2"):
            icol = 1
            type = "artist:"
        if(col == "#3"):
            icol = 2
            type = "album:"

        record = item['values']
        print("col: " + col + " Value: " + record[icol] + " Tags: " + ' '.join(tags))
        # show a message
        # showinfo(title='Information', message=','.join(record))
        # showinfo(title='Information', message=record[col])

        doSearch(type, record[icol], True)

# button play
def btPlay_Click(event):
    sp.start_playback()

# button pause
def btPause_Click(event):
    sp.pause_playback()

# button Vol -
def btVolMinus_Click(event):
    global Volume
    Volume = Volume - 5
    if(Volume < 0):
        Volume = 0
    lbVol.config(text=str(Volume))
    sp.volume(Volume)

# button Vol +
def btVolPlus_Click(event):
    global Volume
    Volume = Volume + 5
    if(Volume > 100):
        Volume = 100
    lbVol.config(text=str(Volume))
    sp.volume(Volume)

# button Quited
def btQuit_Click(event):
    root.quit()


def doSearch(type, value, exact):
    if(exact == True):
        results = sp.search(type + "\"" + value + "\"", limit = 50)  
    else:
        results = sp.search(type +        value       , limit = 50)  


    # check if there is anything at all
    if(any(results)):
        trResult.delete(*trResult.get_children())
        trackURIs = []
        for idx, track in enumerate(results['tracks']['items']):
            # pprint(track)
            # print(idx, track['name'], track['uri'] )
            track_id      = track['uri']
            track_name    = track['name']
            artist_id     = track['artists'][0]['uri']
            artist_name   = track['artists'][0]['name']
            album_id      = track['album']['uri']
            album_name    = track['album']['name']

            trResult.insert('', tk.END, values=(track_name, artist_name, album_name), tags=(track_id, artist_id, album_id))
            trackURIs.append(track['uri'])

        # sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=trackURIs)   


# a background task fetching the current playback and showing it at the 2nd line of the display
def show_current_playback():
    global sp
    while True:
        x = sp.current_playback("DE")
        if((x != None) and (any(x))):
            it = x.get("item")
            if(any(it)):
                tit = it["name"]
                art = it["artists"][0]["name"]
                alb = it["album"]["name"]

                if(any(tit)):
                    lbTitel.config(text=tit)

                if(any(art)):
                    lbArtist.config(text=art)

                if(any(alb)):
                    lbAlbum.config(text=alb)
        sleep(1)



################################################# main ##################################################################
root = tk.Tk()
root.title("Infiloo Spot")
# width = root.winfo_screenwidth()               
# height= root.winfo_screenheight()               
# root.geometry("%dx%d" % (width, height))

''' Search bar '''
frame1 = tk.Frame(root)
frame1.pack(fill=tk.X)

btBack = tk.Button(frame1, text="<<<", width=6)
btBack.pack(side=tk.LEFT, padx=5)

cbType = ttk.Combobox(frame1)
cbType['state'] = 'readonly'
cbType.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)
cbType['values'] = ('Tilte', 'Artist', 'Album', 'Playlists')
cbType.current(newindex=0)
cbType.bind("<<ComboboxSelected>>", cbType_Select)

cbSearch = ttk.Combobox(frame1)
cbSearch['state'] = 'normal'
cbSearch.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

btGo = tk.Button(frame1, text="Go", width=6)
btGo.pack(side=tk.RIGHT, padx=5)

''' Result list and playlist '''
frame2 = tk.Frame(root)
frame2.pack(fill=tk.BOTH, expand=True)

frame21 = tk.Frame(frame2)
frame21.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

columns = ('Titel', 'Artist', 'Album')
trResult = ttk.Treeview(frame21, columns=columns, show='headings')
trResult.heading('Titel',  text='Titel')
trResult.heading('Artist', text='Artist')
trResult.heading('Album',  text='Album')
trResult.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
trResult.bind('<<TreeviewSelect>>', trResult_Select)

frame22 = tk.Frame(frame2)
frame22.pack(side=tk.RIGHT)

btMinus = tk.Button(frame22, text="-", width=5)
btMinus.pack(side=tk.TOP, padx=5)

lbIndex = tk.Label(frame22, text="0", width=5)
lbIndex.pack(side=tk.TOP, padx=5)

btPlus = tk.Button(frame22, text="+", width=5)
btPlus.pack(side=tk.BOTTOM, padx=5)

''' Current playing and volume'''
frame3 = tk.Frame(root)
frame3.pack(fill=tk.X)

frame31 = tk.Frame(frame3)
frame31.pack(side=tk.LEFT)

frame32 = tk.Frame(frame3)
frame32.pack(side=tk.LEFT)

frame33 = tk.Frame(frame3)
frame33.pack(side=tk.LEFT, fill=tk.X, expand=True)

btPlay = tk.Button(frame31, text=">>", width=5)
btPlay.pack(side=tk.TOP, padx=5)
btPlay.bind('<Button-1>', btPlay_Click)

btPause = tk.Button(frame31, text="||", width=5)
btPause.pack(side=tk.TOP, padx=5)
btPause.bind('<Button-1>', btPause_Click)


lbTitelLb = tk.Label(frame32, text="Titel:", width=5, anchor='w')
lbTitelLb.pack(side=tk.TOP, padx=5)

lbTitel = tk.Label(frame33, text="aktueller Titel", width=5, anchor='w')
lbTitel.pack(side=tk.TOP, fill=tk.X, padx=5)


lbArtistLb = tk.Label(frame32, text="Artist:", width=5, anchor='w')
lbArtistLb.pack(side=tk.TOP, padx=5)

lbArtist = tk.Label(frame33, text="aktueller Artist", width=5, anchor='w')
lbArtist.pack(side=tk.TOP, fill=tk.X, padx=5)


lbAlbumLb = tk.Label(frame32, text="Album:", width=5, anchor='w')
lbAlbumLb.pack(side=tk.TOP, padx=5)

lbAlbum = tk.Label(frame33, text="aktuelles Album", width=5, anchor='w')
lbAlbum.pack(side=tk.TOP, fill=tk.X, padx=5)

''' volume control'''
frame34 = tk.Frame(frame3)
frame34.pack(side=tk.RIGHT)

btVolMinus = tk.Button(frame34, text="-", width=5)
btVolMinus.pack(side=tk.TOP, padx=5)
btVolMinus.bind('<Button-1>', btVolMinus_Click)

lbVol = tk.Label(frame34, text="0", width=5)
lbVol.pack(side=tk.TOP, padx=5)
lbVol.config(text=str(Volume))

btVolPlus = tk.Button(frame34, text="+", width=5)
btVolPlus.pack(side=tk.BOTTOM, padx=5)
btVolPlus.bind('<Button-1>', btVolPlus_Click)

''' Add to playlists'''
frame4 = tk.Frame(root)
frame4.pack(fill=tk.X)

lbAddPlayLb = tk.Label(frame4, text="Add to playlist:")
lbAddPlayLb.pack(side=tk.LEFT, padx=5)

cbAddPlay = ttk.Combobox(frame4)
cbAddPlay['state'] = 'readonly'
cbAddPlay.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)   

btGo = tk.Button(frame4, text="Add", width=6)
btGo.pack(side=tk.LEFT, padx=5)

''' Quit'''
btQuit = tk.Button(frame4, text="Quit", width=5)
btQuit.pack(side=tk.RIGHT, padx=5, pady=5)
btQuit.bind('<Button-1>', btQuit_Click)



# init and connect to spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",         # infiloospot client id
                                            client_secret="bb988ada317e44e9a1a73f0b7accf06c",        # infiloospot secret
                                            redirect_uri="http://127.0.0.1:9090",                    # not needed
                                            scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"))    # request permissions that we need
# Shows playing spotify connect devices
res = sp.devices()
pprint(res)

# fill add to playlist combobox
playlists   = sp.current_user_playlists(50, 0)          # fetch playlists from user account
list = []
for idx, item in enumerate(playlists['items']):
    #     print(idx, item['name'] + " - " + item["id"])
    list.append(item['name'])
cbAddPlay['values'] = list      
cbAddPlay.set(list[0])

# start background thread diplsaying the current playback data
start_new_thread(show_current_playback, ())

# sample search to fill the list
doSearch("artist:", "woods of birnam", False)  

# run
root.mainloop()