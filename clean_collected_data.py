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
        float_list = ['comment_likes', 'comment_retweets', 'comment_replies']
        for x in float_list:
            data[x] = convert_str(data[x])
        data = data[data['comment'].notna()]
        data['sentiments'] = generate_sentiments(data)
        X = data['comment']
        y = data['comment_likes']
        z = data['sentiments']
        small_data = pd.DataFrame(list(zip(X[:5], y[:5], z[:5])), columns=['Comment', 'Comment Likes', 'Comment Sentiment Score'])

        # Add logging statements
        print("Data preprocessing successful.")
        
        # Print the head of the small_data DataFrame
        print("Small DataFrame head:")
        print(small_data.head())

        return data, small_data
    except Exception as e:
        print("Error during data preprocessing:", str(e))
        return pd.DataFrame(), pd.DataFrame()


data, small_data = preprocess_data()
print(data.head())
