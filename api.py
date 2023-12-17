# api.py

import tweepy
from api_credentials import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

def fetch_twitter_data(url):
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # Extract tweet ID from the tweet URL
    tweet_id = url.split('/')[-1]

    # Fetch tweet data
    tweet = api.get_status(tweet_id, tweet_mode="extended")

    # Extract relevant information (you might need to adjust this based on your requirements)
    user = tweet.user.screen_name
    created_at = tweet.created_at
    text = tweet.full_text

    # Construct a dictionary with the fetched data
    twitter_data = {'user': user, 'created_at': created_at, 'text': text}

    return twitter_data
