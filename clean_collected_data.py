# clean_collected_data.py

import pandas as pd
from textblob import TextBlob

def convert_str(col):
    col = col.astype(str).str.replace(',', '').str.replace(r'\s*M', 'e6', regex=True).str.replace(r'\s*K', 'e3', regex=True)
    col = col.replace({'K': '*1e3', 'M': '*1e6'}, regex=True)
    return pd.to_numeric(col, errors='coerce')

def generate_sentiments(data):
    # Sentiment analysis using TextBlob
    sentiment_scores = data['comment'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    return sentiment_scores

def preprocess_data():
    try:
        data = pd.read_csv(r'C:\Users\vansh\Desktop\Twitter_customer\collected_data.csv')
        data = data.fillna('0')
        float_list = ['comment_likes', 'comment_retweets', 'comment_replies', 'follower_count']
        for x in float_list:
            data[x] = convert_str(data[x])
        data = data[data['comment'].notna()]
        data['sentiments'] = generate_sentiments(data)
        data['user_engagement'] = data['comment_likes'] + data['comment_retweets'] + data['comment_replies']
        data['average_engagement_per_follower'] = data['user_engagement'] / data['follower_count']
        
        # Calculate average reply depth
        data['reply_depth'] = data['reply_to'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
        average_reply_depth = data.groupby('username')['reply_depth'].mean().reset_index()
        average_reply_depth.columns = ['username', 'average_reply_depth']
        data = pd.merge(data, average_reply_depth, on='username', how='left')
        
        # Add logging statements
        print("Data preprocessing successful.")
        
        # Print the head of the DataFrame
        print("DataFrame head:")
        print(data.head())

        return data
    except Exception as e:
        print("Error during data preprocessing:", str(e))
        return pd.DataFrame()

data = preprocess_data()
