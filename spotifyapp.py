import spotipy
import streamlit as st 
import numpy as np
import os 
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
import requests
import pandas as pd 

st.set_page_config(
    page_title="Spotify Song Analyser",
    page_icon="random",
    layout="wide"
)



SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
    client_id = SPOTIPY_CLIENT_ID, 
    client_secret = SPOTIPY_CLIENT_SECRET
    )
)
    
'''
# Spotify Song Analyser :notes: :saxophone:

Input a song title & the app will return the features of the song as well as recommendations.

Data is fetched from the Python library [*Spotipy*](https://spotipy.readthedocs.io/en/2.18.0/) which is based off the 
[Spotify Web API.](https://developer.spotify.com/documentation/web-api/)
The data is then put into a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) and graphed using [Pandas Chart Visualization](https://pandas.pydata.org/pandas-docs/stable/user_guide/visualization.html). 

'''

image, stats = st.beta_columns(2)

with image:
    song = st.text_input("Enter a song title", value="What's the Use Mac Miller")
    search = sp.search(q='track:'+song, type='track')
    try:
        track_id = search['tracks']['items'][0]['id'] #gets track id 
        track_album = search['tracks']['items'][0]['album']['name'] #gets track album name
        track_image = search['tracks']['items'][0]['album']['images'][0]['url'] #gets track image URL
        track_artist_name = search['tracks']['items'][0]['artists'][0]['name'] #gets the artist for the track 
        track_name = search['tracks']['items'][0]['name'] #gets the track name 

        button = st.selectbox('Display', ('Analyze', 'Reccommend'))
        url_to_song = "https://open.spotify.com/track/" + track_id
        st.write(f"Stream {track_name} by {track_artist_name}: {url_to_song}") #change to cleaner URL?
        r = requests.get(track_image)
        open('img/'+track_id+'.jpg', 'w+b').write(r.content)
        image = Image.open('img/'+track_id+'.jpg')
        st.image(image, caption=f"{track_artist_name} - {track_album}",
                use_column_width='auto')

    except IndexError or NameError:
        st.error("This error is likely due to the API being unable to find the song. Perhaps try to retype it using the song title followed by artist without any hyphens (e.g. In my Blood Shawn Mendes)")
    
with stats:
    if button == "Analyze":
        #st.pyplot(fig=None)
        feat = sp.audio_features(tracks=[track_id])
        features = feat[0]
        p = pd.Series(features).to_frame()
        data_feat = p.loc[['acousticness', 'danceability', 'energy', 'liveness', 'speechiness', 'valence',]]
        bpm = p.loc[['tempo']]
        f = bpm.values[0]
        s = f.item()
        ticks = np.linspace(0,1,11)

        plot = data_feat.plot.barh(xticks=ticks,legend=False) #using Pandas plotting 
        plot.set_xlabel('Scale')
        plot.set_ylabel('Features')
        plot.set_title(f'Spotify Song Analysis for {track_name} by {track_artist_name}')
        plot.invert_yaxis()
        st.pyplot(plot.figure) #https://github.com/streamlit/streamlit/issues/796

        st.subheader(f"BPM (Beats Per Minute): {s}")
        #checkbox
        st.empty()
        box = st.checkbox("What do these mean?")

        if box: 

            '''
            **Acousticness**: A measure of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.
            
            **Danceability**: Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. 
                        A value of 0.0 is least danceable and 1.0 is most danceable.

            **Energy**: A perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. 
                        For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, 
                        perceived loudness, timbre, onset rate, and general entropy.

            **Liveness**: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. 
                        A value above 0.8 provides strong likelihood that the track is live.

            **Speechiness**: Detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), 
                        the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 
                        describe tracks that may contain both music and speech. Values below 0.33 most likely represent music and other non-speech-like tracks.

            **Valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), 
                        while tracks with low valence sound more negative (e.g. sad, depressed, angry).
            
            *As referenced in the [Spotify Web API](https://developer.spotify.com/documentation/web-api/reference)*
            '''

    else: 
        st.subheader(f"Recommendations based off {track_name} by {track_artist_name}")

        recco = sp.recommendations(seed_artists=None, seed_tracks=[track_id], seed_genres=[], limit=10)
    
        for songs in recco['tracks']:
            st.write(f"\"{songs['name']}\" - {songs['artists'][0]['name']}")
            image_reco = requests.get(songs['album']['images'][2]['url'])
            open('img/'+songs['id']+'.jpg', 'w+b').write(image_reco.content)
            st.image(Image.open('img/'+songs['id']+'.jpg'))

'''
### Remarks:
- There are times where the API just cannot find songs and you will have to more specific in the search (e.g. artist name and or album).
    - For example, searching for 'The 1975 Robbers live at the O2' yields no results but 'Robbers The 1975 DH00278' will (as DH00278 is the album).
- There are also instances where inputting a search will yield the wrong version of the song. 
    - For example, 'Shawn Mendes In my Blood' yields an insrumental vesion by Vox Freaks while searching for 'In my Blood Shawn Mendes' yields the correct version.
- For the recommendations portion of the app, some songs that are either new or low on listens will not load recommendations.

### Thank you for viewing! :grinning: 
#### Created by [Thomas Lee](https://thomsmd.ca). View on GitHub [here.](https://github.com/thomaslee01/st.spotify)
'''