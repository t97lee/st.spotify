#in dev you should put these ID's into environment variables 
import spotipy

import streamlit as st 
import numpy as np
import os 
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
import requests
import matplotlib.pyplot as plt #this is not needed? 
import pandas as pd 

client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
    client_id = client_id, 
    client_secret = client_secret
    ))


'''
# Spotify Song Analyzer :notes: :saxophone:

Input a song title & the app will return the features of the song as well as recommendations.

It is currently fetching data from the Python library [*Spotipy*](https://spotipy.readthedocs.io/en/2.18.0/) which is based off the 
[Spotify Web API.](https://developer.spotify.com/documentation/web-api/)

The data is parsed using [Pandas](https://pandas.pydata.org/) and then graphed using [matplotlib](https://matplotlib.org/) pyplot. 

'''
song = st.text_input("Enter some text here", value="BBIBBI")

search = sp.search(q='track:'+song, type='track')

#print(search)
try:
    track_id = search['tracks']['items'][0]['id']
    track_album = search['tracks']['items'][0]['album']['name']
    track_image = search['tracks']['items'][0]['album']['images'][1]['url']
except IndexError:
    st.error("This is an error")
## button interface

r = requests.get(track_image)
open('img/'+track_id+'.jpg', 'wb').write(r.content)

image = Image.open('img/'+track_id+'.jpg')
st.sidebar.image(image, caption=track_album,
        use_column_width=True)
        
btn = st.selectbox('Display', ('Analyze', 'Reccommend'))

if btn == "Analyze":
    #st.pyplot(fig=None)
    url_to_song = "https://open.spotify.com/track/" + track_id
    st.write("Play: " + url_to_song) #change to cleaner URL?

    feat = sp.audio_features(tracks=[track_id]) #Song: Beautiful People - Ed Sheeran 
    features = feat[0]
    p = pd.Series(features).to_frame()
    data_feat = p.loc[['danceability','energy','speechiness','acousticness','valence','liveness']]
    

    ticks = np.linspace(0,1,11)

    plot = data_feat.plot.barh(figsize=(8,8),xticks=ticks,legend=False) #using Pandas plotting 
    plot.set_xlabel('Scale')
    plot.set_ylabel('Features')
    plot.set_title(f'Spotify Song Feature - {song}')
    st.pyplot(plot.figure)

    ##checkbox
    box = st.checkbox("What do these mean?")
    if box: #switch to markdown to support tables?
        st.write("**Acousticness**: A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.")

        st.write("**Liveness**: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live." 
                 "A value above 0.8 provides strong likelihood that the track is live.")

        st.write("**Valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric)," 
                 "while tracks with low valence sound more negative (e.g. sad, depressed, angry).")

        st.write("**Speechiness**: Detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry)," 
                 "the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 " 
                 "describe tracks that may contain both music and speech. Values below 0.33 most likely represent music and other non-speech-like tracks.")

        st.write("**Energy**: Measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy." 
                 "For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, " 
                 "perceived loudness, timbre, onset rate, and general entropy. ")

        st.write("**Danceability**: Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity." 
                 "A value of 0.0 is least danceable and 1.0 is most danceable.")

else: 

    st.write("Reccommendations")

    try:
        rr = sp.recommendations(seed_artists=None, seed_tracks=[track_id], seed_genres=[], limit=5)
    
        for songs in rr['tracks']:
            st.write(f"\"{songs['name']}\" - {songs['artists'][0]['name']}")

            r = requests.get(songs['album']['images'][2]['url'])

            open('img/'+songs['id']+'.jpg', 'wb').write(r.content)

            st.image(Image.open('img/'+songs['id']+'.jpg'), width=64)


    except NameError:
        st.error("This is another error")
