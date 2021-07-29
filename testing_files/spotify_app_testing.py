#testing API calls 
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

c_id = os.environ.get('client_id')
c_sec = os.environ.get('client_secret')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=c_id, client_secret=c_sec))

rr = sp.recommendations(seed_artists='', seed_tracks=['5xrtzzzikpG3BLbo4q1Yul'], seed_genres=[], limit=10)


#print(rr)

#for song in rr['tracks']:
#    print('https://open.spotify.com/track/'+song['id'])

songs_list = []
for song in rr['tracks']:
    songs_list.append(song['name'])

artist_list = []
for artist in rr['tracks']:
    artist_list.append(artist['album']['artists'][0]['name'])

pairs = [pair for pair in zip(artist_list, songs_list)]
print(pairs)

    #x.append(recco['id'])
x = rr['tracks'][0]['album']['images'][0]['url'] #gets the album art, put [1] for smaller img 
print(x)
track_album = rr['tracks'][0]['album']['name']
artist_name = rr['tracks'][0]['album']['artists'][0]['name']
print(track_album)
print(artist_name + " - " + track_album)