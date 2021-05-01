import requests, json, time
import numpy as np
import pandas as pd
from datetime import datetime

def main():
    today = datetime.today().strftime("%b-%d-%Y") # date of data collection
    max_num = 200000
    BEARER_TOKEN = "" # Twitter TOKEN HERE
    df = pd.DataFrame(columns=['id','timestamp','text','user_id'])
    response = search_twitter('bitcoin lang:en -has:links -is:retweet -is:reply -is:quote -has:hashtags', {"tweet.fields":"text,author_id,created_at"}, bearer_token = BEARER_TOKEN)
    df = add_to_df(df,response)
    print(df.index)
    time.sleep(3)
    try:
        while 'next_token' in response['meta'].keys() and df.index.stop <= max_num:
            response = search_twitter('bitcoin lang:en -has:links -is:retweet -is:reply -is:quote -has:hashtags', \
                {"tweet.fields":"text,author_id,created_at","next_token":str(response['meta']['next_token'])}, bearer_token = BEARER_TOKEN)
            df = add_to_df(df,response)
            print(df.index)
            time.sleep(3)
    except (Exception,KeyboardInterrupt) as e:
        print(e)
        df.to_csv(f"twitter-{today}.csv",index=False)
    df.to_csv(f"twitter-{today}.csv",index=False)

def add_to_df(df,response):
    for data in response['data']:
        new_row = pd.DataFrame([[data['id'], data['created_at'], data['text'], data['author_id']]], columns = ['id','timestamp','text','user_id'])
        df = df.append(new_row, ignore_index=True)
    return df

def search_twitter(query, optional, maxNum = 100, bearer_token = None):
    headers = {"Authorization": "Bearer {}".format(bearer_token)} #AUTH
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results={maxNum}"
    # add to query options
    for option, value in optional.items():
        url = url+ str(f"&{option}={value}")
    response = requests.request("GET", url, headers=headers)
    # print(response.status_code) # testing pt
    
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()



if __name__=="__main__":
    main()