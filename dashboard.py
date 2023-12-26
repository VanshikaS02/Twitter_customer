import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from bot import main
from get_sentimet import generate_sentiments
from clean_collected_data import preprocess_data
from plotly.graph_objects import rgb

URL = 'https://twitter.com/elonmusk/status/1388693126206918658'
usr = "VANSHIKASA21372"  
pwd = ""  
file_path = r'C:\Users\vansh\Desktop\Twitter_customer\collected_data.csv'

dash_app = dash.Dash(__name__)

dash_app.layout = html.Div([
    dcc.Graph(id="sentiment-time-series-chart"),
    dcc.Graph(id="user-comment-insights"),
    dcc.Graph(id="Top-Tweets-Insights"),
    dcc.Input(id="input-url", type="url", value=URL),
])

@dash_app.callback(
    Output('sentiment-time-series-chart', 'figure'),
    Output('user-comment-insights', 'figure'),
    Output('Top-Tweets-Insights', 'figure'),
    Input('input-url', 'value'))

def update_insights(url):
    try:
        main(usr, pwd, file_path, url)
        df, small_df = preprocess_data()

        print("Data retrieved successfully.")
        print("Creating Figure 1...")
        
        if df.empty:
            print("DataFrame 'df' is empty.")
        
        fig1 = go.Figure(data=go.Scatter(x=df['datetime'], y=df['sentiments'], mode='markers', marker_color=df['sentiments'], text=df['username']))
        fig1.update_layout(title='Sentiment analysis with Tweet Replies Date Time',
                           xaxis=dict(title='Date Time', gridcolor='lightgrey'),
                           yaxis=dict(title='Sentiment Score', showgrid=False),
                           plot_bgcolor='rgba(0,0,0,0)')

        print("Creating Figure 2...")
        if df.empty:
            print("DataFrame 'df' is empty.")
        
        fig2 = px.scatter(df, x="comment_likes", y="comment_retweets", size="comment_replies", color="sentiments", hover_name="comment", log_x=True)
        fig2.update_layout(title='Reply Statistics Table: Reply Retweets, Reply Likes, Reply Comment Count', plot_bgcolor='rgba(0,0,0,0.1)', yaxis=dict(showgrid=False))
        
        colors = [rgb(239, 243, 255), rgb(189, 215, 231), rgb(107, 174, 214), rgb(49, 130, 1809), rgb(8, 81, 156)]
        small_df['Color'] = colors 

        print("Creating Figure 3...")
        if small_df.empty:
            print("DataFrame 'small_df' is empty.")
        
        fig3 = go.Figure(data=[go.Table(
            header=dict(
                values=["comment", "comment_likes", "comment_sentiment"],
                line_color='white', fill_color='white',
                align='center', font=dict(color='black', size=12)
            ),
            cells=dict(
                values=[small_df['Comment'], small_df['Comment Likes'], small_df['Comment Sentiment Score']],
                line_color=[small_df.Color], fill_color=[small_df.Color],
                align='center', font=dict(color='black', size=11)
            ))
        ])
        fig3.update_layout(title='Popular User Statistics')

        return fig1, fig2, fig3

    except Exception as e:
        print("Error during update_insights:", str(e))
        return go.Figure(), go.Figure(), go.Figure()

if __name__ == "__main__":
    dash_app.run_server(debug=True)
    
