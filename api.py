# api.py

import tweepy
import pandas as pd
from api_credentials import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

def get_api():
    # Set up Tweepy API credentials
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def get_engagement_data(api, tweet_id_list):
    # Initialize lists to store engagement data
    retweets_list = []
    likes_list = []

    # Iterate through tweet IDs and fetch engagement data
    for tweet_id in tweet_id_list:
        try:
            tweet = api.get_status(tweet_id, tweet_mode="extended")
            retweets_list.append(tweet.retweet_count)
            likes_list.append(tweet.favorite_count)
        except tweepy.TweepError as e:
            print(f"Error fetching engagement data for tweet {tweet_id}: {str(e)}")
            retweets_list.append(0)
            likes_list.append(0)

    # Create a DataFrame with engagement data
    engagement_data = pd.DataFrame({
        'tweet_id': tweet_id_list,
        'retweets': retweets_list,
        'likes': likes_list
    })

    return engagement_data

def fetch_twitter_data(api, url):
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

if __name__ == "__main__":
    # Example usage
    api = get_api()
    
    # Example 1: Get engagement data for a list of tweet IDs
    tweet_id_list = ["123456789", "987654321"]
    engagement_data = get_engagement_data(api, tweet_id_list)
    print("Engagement Data:")
    print(engagement_data)

    # Example 2: Fetch Twitter data for a given URL
    url = "https://twitter.com/narendrasharrma/status/1148196782943293441"
    twitter_data = fetch_twitter_data(api, url)
    print("\nTwitter Data:")
    print(twitter_data)
