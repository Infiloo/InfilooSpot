import sys
import spotipy
import spotipy.util as util

scope = 'user-library-read'
token = util.prompt_for_user_token('Icicle', 
                                   scope,
                                   client_id='680ca5403c694cac9f37b459353cbaeb',
                                   client_secret='bb988ada317e44e9a1a73f0b7accf06c',
                                   redirect_uri='http://127.0.0.1:9090')

sp = spotipy.Spotify(auth=token)
results = sp.current_user_saved_tracks()
for item in results['items']:
    track = item['track']
    print(track['name'] + ' - ' + track['artists'][0]['name'])

