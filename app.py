from flask import Flask, render_template, url_for, request, redirect, session
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import plotly.graph_objects as go
from get_sentimet import generate_sentiments
from clean_collected_data import preprocess_data
from selenium.webdriver.chrome.options import Options
import os
import plotly.graph_objects as go
from dash import no_update

from api import fetch_twitter_data, API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET  
import tweepy

chrome_options = Options()
chrome_options.binary_location = str(os.environ.get("GOOGLE_CHROME_BIN"))

URL = ''
usr = ""
pwd = ""
file_path = r'C:\Users\vansh\Desktop\Twitter_customer\collected_data.csv'

markdown_text1 = '''
# Insights on your Twitter Post

The dashboard presents visuals on the analysis conducted on the user response data on your Twitter post. 
The dashboard gives an overview of the sentiment analysis of the tweet replies recorded over the span of the posting date and today.

## Sentiment Analysis
The first graph depicts **Sentiment Analysis of Replies** on your Twitter post. This graph shows how the sentiments 
of the reactions of users on your post have changed or evolved over time. This graph is useful to understand the Twitter post popularity
over time and general reaction over time.
'''

markdown_text2 = '''
## User Comment Insights
The second graph depicts **User Data Statistics** on your Twitter post. This graph shows the popular reply stats on your post
that may prove useful as an important customer review feedback. The graph plots 3 useful features: reply user likes, comments, and retweets, 
hovered by the reply comment for reference. This is a very valuable customer review graph.
'''

markdown_text3 = '''
## Popular Reply  Sentiments
The third graph shows a tabular representation of the **Sentiments of the five most popular by likes user comments** on your tweet. These statistics give 
insight into the general impression of your post. A very good popular post makes a good impression about your Twitter post, while a 
negative feedback may prove useful to your company.
'''
markdown_text4 = '''
## User engagement 
The fourth graph shows different user engagements such as retweets, likes, and comments.
'''
markdown_text5 = '''
## Top users engagement 
The fifth graph generates insights into the engagement metrics for the top users who interacted with a specific tweet. 
'''

markdown_text6 = '''
## Average engagement per follower 
The sixth graph is a measure of how actively engaged a user's followers are with their content on a platform. It is calculated by dividing the total engagement (likes, retweets, and comments) a user receives by the number of followers they have. The resulting value represents the average engagement each follower provides.
'''
markdown_text7 = '''
## Reply depth 
The seventh graph indicates how many levels of replies exist in response to an original post or tweet. Each reply to the original post increases the reply depth by one level.
'''
#def get_data(url):
#    try:
#        # Fetch Twitter data using Tweepy
#        twitter_data = fetch_twitter_data(url)  # Implement this function in api.py
#        # Process the data as needed
#        data, small_data = preprocess_data(twitter_data)
#        return data, small_data
#    except Exception as e:
#        print("Error during data retrieval:", str(e))
#        return pd.DataFrame(), pd.DataFrame()

def get_data(url):
    try:
        twitter_data = fetch_twitter_data(url)
        # Process twitter_data as needed
        data, small_data = preprocess_data(twitter_data)  # Assuming preprocess_data() takes twitter_data as an argument
        return data, small_data
    except Exception as e:
        print("Error during data retrieval:", str(e))
        return pd.DataFrame(), pd.DataFrame()
    
server = Flask(__name__)
server.secret_key = "abc" 

dash_app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/' )

dash_app.layout = html.Div([
    dcc.Markdown(children=markdown_text1),
    dcc.Graph(id="sentiment-time-series-chart"),
    dcc.Markdown(children=markdown_text2),
    dcc.Graph(id="user-comment-insights"),
    dcc.Markdown(children=markdown_text3),
    dcc.Graph(id="Top-Tweets-Insights"),
    dcc.Input(id="input-url", type="url", value=URL),
    dcc.Graph(id="user-engagement"),
    dcc.Markdown(children=markdown_text4),
    dcc.Graph(id="top-users-engagement"),
    dcc.Markdown(children=markdown_text5),
    dcc.Graph(id="average-engagement-per-follower"),
    dcc.Markdown(children=markdown_text6),
    dcc.Graph(id="reply-depth"),
    dcc.Markdown(children=markdown_text7),
])

@dash_app.callback (
    Output('figure1', 'figure'),
    Output('figure2', 'figure'),
    Output('figure3', 'figure'),
    Output('figure4', 'figure'),
    Output('figure5', 'figure'),
    Output('average-engagement-per-follower', 'figure'),
    Output('reply-depth', 'figure'),
    Input('input-url', 'value')
)

def update_engagement_insights(url):
    try:
        # Retrieve data
        df, small_df = get_data(url)
        print("Data retrieved successfully.")
    except Exception as e:
        print("Error retrieving data:", str(e))
        return no_update, no_update
    
    # Create Figure 1: Sentiment Analysis Time Series Chart
    try:
        print("Creating Figure 1...")
        if not df.empty:
            fig1 = go.Figure(data=go.Scatter(x=df['datetime'], y=df['sentiments'], mode='markers', marker_color=df['sentiments'], text=df['username']))
            fig1.update_layout(title='Sentiment analysis with Tweet Replies Date Time',
                               xaxis=dict(title='Date Time', gridcolor='lightgrey'),
                               yaxis=dict(title='Sentiment Score', showgrid=False),
                               plot_bgcolor='rgba(0,0,0,0)')
            print("Figure 1 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig1 = go.Figure()
    except Exception as e:
        print("Error creating Figure 1:", str(e))
        fig1 = go.Figure()

    # Create Figure 2: User Comment Insights Scatter Plot
    try:
        print("Creating Figure 2...")
        if not df.empty:
            fig2 = px.scatter(df, x="comment_likes", y="comment_retweets", size="comment_replies", color="sentiments", hover_name="comment", log_x=True)
            fig2.update_layout(title='Reply Statistics Table: Reply Retweets, Reply Likes, Reply Comment Count', plot_bgcolor='rgba(0,0,0,0.1)', yaxis=dict(showgrid=False))
            print("Figure 2 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig2 = go.Figure()
    except Exception as e:
        print("Error creating Figure 2:", str(e))
        fig2 = go.Figure()

    # Create Figure 3: Top Tweets Insights Table
    try:
        print("Creating Figure 3...")
        if not small_df.empty:
            colors = ['rgb(239, 243, 255)', 'rgb(189, 215, 231)', 'rgb(107, 174, 214)', 'rgb(49, 130, 189)', 'rgb(8, 81, 156)']
            small_df['Color'] = colors
            fig3 = go.Figure(data=[go.Table(header=dict(values=["comment", "comment_likes", "comment_sentiment"],
                                                        line_color='white', fill_color='white',
                                                        align='center', font=dict(color='black', size=12)),
                                            cells=dict(values=[small_df['Comment'], small_df['Comment Likes'], small_df['Comment Sentiment Score']],
                                                       line_color=[small_df.Color], fill_color=[small_df.Color],
                                                       align='center', font=dict(color='black', size=11)))
                                   ])
            fig3.update_layout(title='Popular User Statistics')
            print("Figure 3 created successfully.")
        else:
            print("DataFrame 'small_df' is empty.")
            fig3 = go.Figure()
    except Exception as e:
        print("Error creating Figure 3:", str(e))
        fig3 = go.Figure()
    
    try:
        # Create Figure 4: User Engagement Time Series Chart
        print("Creating Figure 4...")
        if not df.empty:
            fig4 = go.Figure(data=go.Scatter(x=df['datetime'], y=df['user_engagement'], mode='lines', line_color='blue'))
            fig4.update_layout(title='User Engagement over Time',
                               xaxis=dict(title='Date Time', gridcolor='lightgrey'),
                               yaxis=dict(title='User Engagement', showgrid=False),
                               plot_bgcolor='rgba(0,0,0,0)')
            print("Figure 4 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig4 = go.Figure()
    except Exception as e:
        print("Error creating Figure 4:", str(e))
        fig4 = go.Figure()

    # Create Figure 5: Top Users by Engagement Table
    try:
        print("Creating Figure 5...")
        if not df.empty:
            top_users_df = df.nlargest(5, 'user_engagement')
            fig5 = go.Figure(data=[go.Table(header=dict(values=["username", "user_engagement"]),
                                           cells=dict(values=[top_users_df['username'], top_users_df['user_engagement']]))
                                   ])
            fig5.update_layout(title='Top Users by Engagement')
            print("Figure 5 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig5 = go.Figure()
    except Exception as e:
        print("Error creating Figure 5:", str(e))
        fig5 = go.Figure()

    try:
        # Create Figure 6: Average Engagement per Follower
        print("Creating Figure 6...")
        if not df.empty:
            fig6 = px.bar(df, x='username', y='average_engagement_per_follower', title='Average Engagement per Follower')
            print("Figure 6 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig6 = go.Figure()
    except Exception as e:
        print("Error creating Figure 6:", str(e))
        fig6 = go.Figure()

    try:
        # Create Figure 7: Reply Depth
        print("Creating Figure 7...")
        if not df.empty:
            fig7 = px.bar(df, x='username', y='average_reply_depth', title='Average Reply Depth')
            print("Figure 7 created successfully.")
        else:
            print("DataFrame 'df' is empty.")
            fig7 = go.Figure()
    except Exception as e:
        print("Error creating Figure 7:", str(e))
        fig7 = go.Figure()

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7
    

@server.route('/')
def index():
    return render_template('index.html')

@server.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        url = request.form.get('Tweet_URL')
        session['url'] = url
    return redirect(url_for('dashboard'))

@server.route('/dashboard/')
def dashboard():
    URL = session['url']
    return redirect('/dash')

app = DispatcherMiddleware(server, {
    '/dash': dash_app.server,
})

run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)
