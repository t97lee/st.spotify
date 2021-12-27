import spotipy
import streamlit as st 
import numpy as np
import os 
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
import requests
import pandas as pd 
from lyricsgenius import Genius
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Spotify Song Analyzer",
    page_icon="random",
    layout="wide"
)

#Genius API
genius_token = os.environ.get('genius_token')
genius = Genius(genius_token)

#Spotify API
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials (
        client_id = SPOTIPY_CLIENT_ID, 
        client_secret = SPOTIPY_CLIENT_SECRET
    )
)
    
'''
# Spotify Song Analyzer

Input a song title & the app will return the features of the song as well as recommendations.

Data is fetched from the Python library [*Spotipy*](https://spotipy.readthedocs.io/en/2.18.0/) which is based off the 
[Spotify Web API.](https://developer.spotify.com/documentation/web-api/)
The data is then put into a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) and graphed using [Pandas Chart Visualization](https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html). 

'''
song = st.text_input("Enter a song title", value="What's the Use Mac Miller")
search = sp.search(q='track:'+song, type='track')

class GetTrackInfo:
    def __init__(self, search):
        self.search = search

    def track_id(self):
        track_id = search['tracks']['items'][0]['id'] #gets track id 
        return track_id
    
    def track_album(self):
        track_album = search['tracks']['items'][0]['album']['name'] #gets track album name
        return track_album

    def track_image(self):
        track_image = search['tracks']['items'][0]['album']['images'][0]['url'] #gets track image URL
        return track_image
    
    def track_artist_name(self):
        track_artist_name = search['tracks']['items'][0]['artists'][0]['name'] #gets the artist for the track 
        return track_artist_name

    def track_name(self):
        track_name = search['tracks']['items'][0]['name'] #gets the track name 
        return track_name

    def track_preview(self):
        track_preview = search['tracks']['items'][0]['preview_url']
        return track_preview

songs = GetTrackInfo(song)

def get_lyrics(song):
    song_lyrics = genius.search_song(songs.track_name(), songs.track_artist_name())
    st.text(song_lyrics.lyrics)
###

def url(song):
    url_to_song = "https://open.spotify.com/track/" + songs.track_id()
    st.write(f"Stream {songs.track_name()} by {songs.track_artist_name()}: {url_to_song}") #change to cleaner URL?

image, stats = st.columns(2)

with image:
    try:
        url(song)
        r = requests.get(songs.track_image())
        open('img/'+songs.track_id()+'.jpg', 'w+b').write(r.content)
        image_album = Image.open('img/'+songs.track_id()+'.jpg')
        st.image(image_album, caption=f"{songs.track_artist_name()} - {songs.track_album()}",
                use_column_width='auto')

    except IndexError or NameError:
        st.error(
            "This error is likely due to the API being unable to find the song. Perhaps try to retype it using the song title followed by artist without any hyphens (e.g. In my Blood Shawn Mendes)"
        )

with stats:
    button = st.selectbox('Choose an option', ('Analyze', 'Recommendations'))
    if button == "Analyze":
        #st.pyplot(fig=None)
        feat = sp.audio_features(tracks=[songs.track_id()])
        features = feat[0]
        p = pd.Series(features).to_frame()
        data_feat = p.loc[['acousticness', 'danceability', 'energy', 'liveness', 'speechiness', 'valence',]]
        bpm = p.loc[['tempo']]
        values = bpm.values[0]
        bpms = values.item()
        ticks = np.linspace(0,1,11)

        plot = data_feat.plot.barh(xticks=ticks,legend=False) #using Pandas plotting 
        plot.set_xlabel('Scale')
        plot.set_ylabel('Features')
        plot.set_title(f'Analysis for {songs.track_name()} by {songs.track_artist_name()}')
        plot.invert_yaxis()
        st.pyplot(plot.figure) #https://github.com/streamlit/streamlit/issues/796
        st.subheader(f"BPM (Beats Per Minute): {bpms}")

        ## checkboxes
        preview_box = st.checkbox("Click to preview the song")
        lyrics_box = st.checkbox(f"Click to show lyrics to {songs.track_name()} by {songs.track_artist_name()}")
        box = st.checkbox("What do these metrics mean?")
    
        if preview_box:
            st.warning("Warning: some audio previews may be very loud and audio volume will reset if the page is refreshed")
            st.audio(songs.track_preview(),format='audio/wav')

        if lyrics_box:
            st.subheader(f"Lyrics for {songs.track_name()} by {songs.track_artist_name()}")
            try:
                get_lyrics(song)
            except AttributeError:
                st.error(f"Unfortunately, the Genius API could not find lyrics for the song {songs.track_name()} by {songs.track_artist_name()} - I am working on fixing this")

        if box:
            st.subheader("Attribute Definitions")
            '''
            **Acousticness**: A measure of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.
            
            **Danceability**: Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. 
                        A value of 0.0 is least danceable and 1.0 is most danceable.

            **Energy**: A perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. 
                        For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, 
                        perceived loudness, timbre, onset rate, and general entropy.

            **Liveness**: Detects the presence of an audience in the rding. Higher liveness values represent an increased probability that the track was performed live. 
                        A value above 0.8 provides strong likelihood that the track is live.

            **Speechiness**: Detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), 
                        the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 
                        describe tracks that may contain both music and speech. Values below 0.33 most likely represent music and other non-speech-like tracks.

            **Valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), 
                        while tracks with low valence sound more negative (e.g. sad, depressed, angry).
            
            *As referenced in the [Spotify Web API](https://developer.spotify.com/documentation/web-api/reference)*
            '''

    else: 
        st.subheader(f"Recommendations based off {songs.track_name()} by {songs.track_artist_name()}")

        reco = sp.recommendations(seed_artists=None, seed_tracks=[songs.track_id()], seed_genres=[], limit=10)
    
        for i in reco['tracks']:
            st.write(f"\"{i['name']}\" - {i['artists'][0]['name']}")
            image_reco = requests.get(i['album']['images'][2]['url'])
            open('img/'+i['id']+'.jpg', 'w+b').write(image_reco.content)
            st.image(Image.open('img/'+i['id']+'.jpg'))

'''
### Remarks:
- There are times where the API just cannot find songs and you will have to more specific in the search (e.g. artist name and or album).
    - For example, searching for 'The 1975 Robbers live at the O2' yields no results but 'Robbers The 1975 DH00278' will (as DH00278 is the album).
- There are also instances where inputting a search will yield the wrong version of the song. 
    - For example, 'Shawn Mendes In my Blood' yields an insrumental vesion by Vox Freaks while searching for 'In my Blood Shawn Mendes' yields the correct version.
- For the recommendations portion of the app, some songs that are either new or low on listens will not load recommendations.
- Lyrics of the songs are found via the LyricsGenius Python library which sometimes cannot find the correct lyrics to songs due to the way I have it set up. 
I am working on fixing this. 
### Thank you for viewing! :grinning: 
#### Created by [Thomas Lee](https://thomsmd.ca). View on GitHub [here.](https://github.com/thomaslee01/st.spotify)
'''