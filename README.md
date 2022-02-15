# InfilooSpot
Simple spotipy based Spotify client using keyboard as input and a 4*20 char LCD2002 as output

It was made to run on a raspberry with a local spotify connect (raspotify).

Usage:
- At 1st start it uses the OAuth service of spotify to get the spotify user account credentials and will create cache a token.
- It will list the the available spotify connect devices on the console so find the one you'd like and use the ID in the code
- In the list of titles skip forward and backward using arrow left and right
- It allows to search for keywords and also narrow the search for title and artist
- It allows to search for an album, lists the found albums one by one in the 1st line. Use enter to select one and it will play it
- It can enumerate the playlists of the current user. You browse through them using the arrow key and select one with Enter
- It shows the current playback title in the 2nd line of the display even when the playback is done on a different device assigned to the current user.

Installation:
- setup spotify connect (raspotify) see    https://github.com/dtcooper/raspotify
- Install spotipy                   see    https://spotipy.readthedocs.io/en/2.18.0/
- Run python InfilooSpot.py

              


