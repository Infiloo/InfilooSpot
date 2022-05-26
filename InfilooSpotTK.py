#spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from pprint import pprint

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo


def item_selected(event):
    real_coords = (tree.winfo_pointerx() - tree.winfo_rootx(),
                   tree.winfo_pointery() - tree.winfo_rooty())
    item = tree.identify('item', *real_coords)

    for selected_item in tree.selection():
        item = tree.item(selected_item)
        tags = item['tags']
        col  = tree.identify_column(real_coords[0])
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



def doSearch(type, value, exact):
    if(exact == True):
        results = sp.search(type + "\"" + value + "\"", limit = 50)  
    else:
        results = sp.search(type +        value       , limit = 50)  


    # check if there is anything at all
    if(any(results)):
        tree.delete(*tree.get_children())
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

            tree.insert('', tk.END, values=(track_name, artist_name, album_name), tags=(track_id, artist_id, album_id))
            trackURIs.append(track['uri'])

        # sp.start_playback('4e6e703f564bfdfcb1c626ebd675b6f26ec90c7d', uris=trackURIs)   



################################################# main ##################################################################
root = tk.Tk()
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
cbType['values'] = ('Tilte', 'Artist', 'Album', 'Playlist')
cbType.current(newindex=0)

cbSearch = ttk.Combobox(frame1)
cbSearch['state'] = 'normal'
cbSearch.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

btGo = tk.Button(frame1, text="Go", width=6)
btGo.pack(side=tk.RIGHT, padx=5)

''' Result list and playlist '''
columns = ('Titel', 'Artist', 'Album')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('Titel',  text='Titel')
tree.heading('Artist', text='Artist')
tree.heading('Album',  text='Album')
tree.pack(padx=10,pady=10,fill=tk.BOTH,expand=True)
tree.bind('<<TreeviewSelect>>', item_selected)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)

# init and connect to spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="680ca5403c694cac9f37b459353cbaeb",         # infiloospot client id
                                            client_secret="bb988ada317e44e9a1a73f0b7accf06c",        # infiloospot secret
                                            redirect_uri="http://127.0.0.1:9090",                    # not needed
                                            scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"))    # request permissions that we need
# Shows playing spotify connect devices
res = sp.devices()
pprint(res)

# sample search to fill the list
doSearch("artist:", "woods of birnam", False)  

# run
root.mainloop()