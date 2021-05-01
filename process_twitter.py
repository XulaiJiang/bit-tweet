from pyspark.sql import SparkSession, Row
spark = SparkSession.builder.getOrCreate()

twitter = spark.read.json('twitter.json')

# RDD based sentiment score converter
def text_to_sent(row):
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    nltk.download("vader_lexicon")
    sid = SentimentIntensityAnalyzer()
    score = sid.polarity_scores(row.text)['compound']
    row_dict = row.asDict()
    row_dict['sentimental_score'] = score 
    return Row(**row_dict)

# RDD based converting datetime to unix epoch
def datetime_to_unix(row):
    from datetime import datetime
    time = row.created_at[:-5].replace('T',' ')
    row_dict = row.asDict()
    row_dict['unix'] = datetime.strptime(time,"%Y-%m-%d %H:%M:%S").timestamp()
    return Row(**row_dict) 

# convert time to unix epoch
twitter = twitter.rdd.map(datetime_to_unix).toDF()
# twitter.show()
# convert text to sentimental score
twitter = twitter.rdd.map(text_to_sent).toDF()
# twitter.show()

twitter.write.csv('twitter_sent.csv')