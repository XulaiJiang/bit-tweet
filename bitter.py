import streamlit as st
import pandas as pd

import requests
from datetime import datetime, date, time, timezone
from dateutil.tz import tzutc

import plotly.graph_objects as go
import plotly.express as px

# Page Config
st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="expanded",  # Can be "auto", "expanded", "collapsed"
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
)

# App title
st.title("BitCoin Vs. Twitter")
st.markdown('''
***Disclaimer***
- This is an app demo designed by [Xulai Jiang](https://github.com/XulaiJiang) using Plotly and Streamlit;
- Private Information, such as *User_Id* from [twitter.com](https://twitter.com), are filtered;
- App is for demonstration purposes only;
''')
st.write('---')
# Sidebar
st.sidebar.subheader('Select Date and Time')
start_time = st.sidebar.time_input('Start Time',time(10,00))
start_date = st.sidebar.date_input("Start date", date(2021, 3, 14))
end_time = st.sidebar.time_input('End Time',time(11,00))
end_date = st.sidebar.date_input("End date", date(2021, 3, 14))
# Convert time to unix for query
start = datetime2unix(start_date,start_time)
end = datetime2unix(end_date,end_time)
# Retrieve data in range
bitcoin = get_df('bitcoin',startAt = str(start), endAt = str(end))
twitter = get_df('twitter',startAt = str(start), endAt = str(end))
# Show dataframes
if (bitcoin is None): # when both are empty
    st.warning('Please choose a valid time between 3/14/2021 to 3/28/2021.')
    st.stop()
elif (twitter is None): # when tweets are empty
    # Show bitcoin data
    color = st.color_picker('Choose a Color for Line Plot:', '#00f5f9')
    st.subheader(f'**Bitcoin Price Between {datetime.combine(start_date,start_time).strftime("%#m/%d/%y %H:%M")} and {datetime.combine(end_date,end_time).strftime("%#m/%d/%y %H:%M")}**')
    fig_scat = go.Figure([go.Scatter(name='Line Chart',x=bitcoin['date'], y=bitcoin['high'],line=dict(color=color, width=2))])
    # Show candle plot on top
    candle = st.checkbox('Show CandleStick Chart')
    if candle:
        fig_scat.add_trace(go.Candlestick(name='Candlestick Chart',x=bitcoin['date'],open=bitcoin['open'],high=bitcoin['high'],low=bitcoin['low'],close=bitcoin['close']))
    # Remove axes
    fig_scat.update_xaxes(showgrid=False)
    fig_scat.update_yaxes(showgrid=False)
    fig_scat.update_layout(xaxis_rangeslider_visible=False)
    # Show plot(s)
    st.plotly_chart(fig_scat)
    show_bit = st.selectbox('Show Original Bitcoin Data?', ('No','Yes'))
    if show_bit == "Yes":
        num_bit = st.slider('Number of Rows:', min_value=10, max_value=len(bitcoin.index))
        st.table(bitcoin[['date','high','low','open','close','Volume USD']].iloc[:num_bit].set_index('date').sort_values(by='date',axis=0,ascending=False))
else: # both not None
    # Show bitcoin data
    color = st.color_picker('Choose a Color for Line Plot:', '#00f5f9')
    st.subheader(f'**Bitcoin Price Between {datetime.combine(start_date,start_time).strftime("%#m/%d/%y %H:%M")} and {datetime.combine(end_date,end_time).strftime("%#m/%d/%y %H:%M")}**')
    fig_scat = go.Figure([go.Scatter(name='Line Chart',x=bitcoin['date'], y=bitcoin['high'],line=dict(color=color, width=2))])
    # Show candle plot on top
    candle = st.checkbox('Show CandleStick Chart')
    if candle:
        fig_scat.add_trace(go.Candlestick(name='Candlestick Chart',x=bitcoin['date'],open=bitcoin['open'],high=bitcoin['high'],low=bitcoin['low'],close=bitcoin['close']))
    # Remove axes
    fig_scat.update_xaxes(showgrid=False)
    fig_scat.update_yaxes(showgrid=False)
    fig_scat.update_layout(xaxis_rangeslider_visible=False)
    # Show plot(s)
    st.plotly_chart(fig_scat)
    show_bit = st.selectbox('Show Original Bitcoin Data?', ('No','Yes'))
    if show_bit == "Yes":
        num_bit = st.slider('Number of Rows:', min_value=10, max_value=len(bitcoin.index))
        st.table(bitcoin[['date','high','low','open','close','Volume USD']].iloc[:num_bit].set_index('date').sort_values(by='date',axis=0,ascending=False))
        
    # Show twitter data
    st.subheader(f'**Sentiment Scores in Tweets**')
    fig_t = px.bar(twitter, x='date', y="sentiment_score", color='sentiment_score')
    st.plotly_chart(fig_t)
    show_sent = st.selectbox('Show Original Twitter Data?', ('No','Yes'))
    if show_sent == "Yes":
        num_twt = st.slider('Number of tweets:', min_value=10, max_value=len(twitter.index))
        st.table(twitter[['date','text','sentiment_score']].iloc[:num_twt].set_index('date').rename(columns={"sentiment_score":"Sentiment Score","text":"Tweet Content"}).sort_values(by='date',axis=0,ascending=False))

# Querying data
def get_df(name,**kwargs):
    url = st.secrets['db_url'] % name
    payload = {'orderBy':'"unix"'}
    for key, value in kwargs.items():
        payload[key] = value
    js = requests.get(url,params=payload).json()
    if js: # when data is not null
        if isinstance(js, dict): # when result is dict 
            df = pd.DataFrame(list(js.values())) 
        elif isinstance(js, list): # when result is list
            df = pd.DataFrame(js)
        df['date'] = df['unix'].apply(unix2datetime)
        df = df.sort_values(by=['unix'],axis=0)
        return df

# Time and Epoch Conversions
def datetime2unix(date,time):
    return datetime.combine(date,time).timestamp()
def unix2datetime(unix):
    return datetime.fromtimestamp(unix).strftime("%#m/%d/%y %H:%M")


if __name__=="__main__":
    main()
