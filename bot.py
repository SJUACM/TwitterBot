import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import tweepy
import json
import requests
import logging
import time
from credentials import access_token, access_token_secret, API_key, API_secret_key, spotify_username, spotify_client_id, spotify_client_secret

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_key, API_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

try:
    api.verify_credentials()
    print("Authentication Successful")
except:
    print("Authentication Error")
   
try:
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    redirect_uri = 'https://google.com'

    token = util.prompt_for_user_token(username=spotify_username, 
                                    scope='playlist-modify-public', 
                                    client_id=spotify_client_id,   
                                    client_secret=spotify_client_secret,     
                                    redirect_uri=redirect_uri)

    sp = spotipy.Spotify(auth=token) 

except Exception as e:
    print(e)
 
   
# For adding logs in application
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)   
    
    
def get_last_tweet(file):
    f = open(file, 'r')
    try:
        lastId = int(f.read().strip())
        f.close()
        return lastId    
    except:
        print('Error')
    
def put_last_tweet(file, Id):
    f = open(file, 'w')
    f.write(str(Id))
    f.close()
    logger.info("Updated the file with the latest tweet Id")
    return 

def respondToTweet(file='tweet_ID.txt'):
    last_id = get_last_tweet(file)
    mentions = api.mentions_timeline(last_id, tweet_mode='extended')
    if len(mentions) == 0:
        return

    new_id = 0
    logger.info("Received a mention...")

    for mention in reversed(mentions):
        logger.info(str(mention.id) + '-' + mention.full_text)
        new_id = mention.id

        if 'ADD_SONG:' in mention.full_text:
            
            logger.info(f"Responding back to -{mention.full_text} from {mention.user.name}")
            
            try:
                tweet = mention.full_text
                artist = tweet.split(':')[1][1:]
                song_name = tweet.split(':')[2][1:]

                search_results = sp.search(q="artist:" + artist + " track:" + song_name, type="track")
                
                queried_artist = search_results['tracks']['items'][0]['artists'][0]['name']
                queried_track_name = search_results['tracks']['items'][0]['name']
                playlist_id = 'spotify:playlist:3rHl8aAOxRJ9AVBb5KMmx7'
                track_uri = search_results['tracks']['items'][0]['uri']

                if artist == queried_artist and song_name == queried_track_name:
                    
                    logger.info("Artist and track name are valid\nLiking and Replying to Tweet...")
                    sp.user_playlist_add_tracks(spotify_username, playlist_id, [track_uri])
                    
                    try:
                        api.create_favorite(mention.id)
                    except Exception as e:
                        print(e)
                    
                    api.update_status(status=f"@{mention.user.screen_name} Added track to playlist!", in_reply_to_status_id=mention.id, auto_populate_reply_metadata=True)
                
                else:
                    
                    logger.info("\nArtist and track do not match up...\n")

                    try:
                        api.create_favorite(mention.id)
                    except Exception as e:
                        print(e)
                        
                    api.update_status(status=f"@{mention.user.screen_name} Error querying track, try again!", in_reply_to_status_id=mention.id, auto_populate_reply_metadata=True)
                
            except:
                logger.info("Already replied to {}".format(mention.id))

    put_last_tweet(file, new_id)
    print()
    
    
while True:
    respondToTweet()
    time.sleep(60)