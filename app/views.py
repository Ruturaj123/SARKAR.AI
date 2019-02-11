from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from newsapi import NewsApiClient
import json
import random
from jack import readers
from jack.core import QASetting
import os
from .custom_tf_idf import *
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import wikipedia
from collections import OrderedDict
import unicodedata
import spacy
from collections import Counter
# Create your views here.
consumer_key = 'K8rDGMdTDwKz2tWpNIuurZSr7'
consumer_secret = 'wb1ZWvuC9loX78f6GVDVgNzoG0YATKLhPwjtXlnWrOiplm901u'
access_token = '962553243116204032-XWr3Ud2mD56izQFWFXu2aZMCZ9MkGxZ'
access_token_secret = 'fqYgYnEAkwy15NZBHhjb0ZCoL67hybGZe7fni8QXFL2RY'


nlp = spacy.load('en_core_web_sm')
document_seen = 99999

def index(request):

    # get_tweets_based_on_location("statue of unity")
    # get_news("demonetization india")
    # get_tweets()
    if request.POST:
        topic = request.POST.get("search")
        if topic != "":
            news = get_news(topic)
            sentiment_categories = news["sentiment_categories"]
            publishers_sentiments = news["publishers_sentiments"]
            print("Publisher sentiments: ", publishers_sentiments)
            percent_overall = analyze_tweets(topic)
            percent_location, percent_location_blog = get_tweets_based_on_location(topic)
            context = {
                "percent_overall": percent_overall,
                "percent_location": percent_location,
                "sentiment_categories": sentiment_categories,
                "publishers_sentiments": publishers_sentiments,
                "percent_location_blog": percent_location_blog,
                "topic": topic
            }
            # print("HELLO")
            #print(news)

            return render(request, 'index.html', context)
    return render(request, 'index.html', {})


def linechart(request):

    return render(request, 'linechart.html', {})



def get_news(topic):
    # topic = "demonetization india"
    api = NewsApiClient(api_key="4e6941abb75c490a950e634acf91ed08")
    all_articles = api.get_everything(q=topic, language='en', sort_by='relevancy')
    publishers_list = {}
    for article in all_articles["articles"]:
        if article["source"]["name"] not in publishers_list and article["content"] is not None:
            publishers_list[article["source"]["name"]] = {"url": "", "content": ""}
            publishers_list[article["source"]["name"]]["url"] =  article["url"]
            publishers_list[article["source"]["name"]]["content"] = article["content"]
            publishers_list[article["source"]["name"]]["sentiment"] = TextBlob(article["content"]).sentiment.polarity

    sentiment_categories = [0, 0, 0]
    print([i for i in publishers_list])
    for i in publishers_list:
        if publishers_list[i]["sentiment"] >= -1 and publishers_list[i]["sentiment"] < -0.2:
            sentiment_categories[0] += 1
        elif publishers_list[i]["sentiment"] >= -0.2 and publishers_list[i]["sentiment"] < 0.2:
            sentiment_categories[1] += 1
        elif publishers_list[i]["sentiment"] >= 0.2:
            sentiment_categories[2] += 1

    # print(sentiment_categories)
    for i in range(len(sentiment_categories)):
        if sentiment_categories[i] == 0:
            sentiment_categories[i] = random.randint(1,3)

    sentiment_categories = [i*100 / sum(sentiment_categories) for i in sentiment_categories]

    # print(sum(sentiment_categories))
    print("fjcbskv")
    print(sentiment_categories)
    # return HttpResponse(json.dumps({'articles': publishers_list, "sentiments": sentiment_categories}), content_type="application/json")
    publishers_sentiments = []

    for i in publishers_list:
        publishers_sentiments.append([i, publishers_list[i]["sentiment"]])

    print(publishers_sentiments)

    return {"sentiment_categories": sentiment_categories, "publishers_sentiments": publishers_sentiments}


def chart(request):
	data = [
				["China", 1882, "#7474F0"],
				["Japan", -33.923036, "#C5C5FD"],
				["Germany", -34.028249, "#952FFE"],
				["UK", -33.80010128657071, "#7474F0"]
			]
	context = {"data": data}
	return render(request, 'linechart.html', context)

def trying(request):
	return render(request, 'trying.html', {})

def render_sports_page(request):
	return render(request, 'sports.html', {})

def render_politics_page(request):
    percent_overall = analyze_tweets("demonetization")
    percent_location = get_tweets_based_on_location("demonetization")

    data = get_news("demonetization india")

    sentiment_categories = data["sentiment_categories"]
    publishers_sentiments = data["publishers_sentiments"]

    context = {
        "percent_overall": percent_overall,
        "percent_location": percent_location,
        "sentiment_categories": sentiment_categories,
        "publishers_sentiments": publishers_sentiments
    }
    return render(request, 'politics.html', context)

def render_gen_politics_page(request):
    return render(request, 'gen-politics.html', {})

def render_gen_sports_page(request):
    return render(request, 'gen-sports.html', {})

def get_tweets_based_on_location(topic):

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    west_tweets = []
    north_tweets = []
    south_tweets = []
    east_tweets = []

    # public_tweets = api.home_timeline()

    west = api.search(q=topic, lang="en", geocode="19.0826881,72.6009809,200km")
    for tweet in west:
        west_tweets.append(tweet)

    north = api.search(q=topic, lang="en", geocode="28.6497991,76.8039719,200km")
    for tweet in north:
        north_tweets.append(tweet)

    south = api.search(q=topic, lang="en", geocode="12.954517,77.3507328,200km")
    for tweet in south:
        south_tweets.append(tweet)

    east = api.search(q=topic, lang="en", geocode="24.7550083,84.3608373,,200km")
    for tweet in east:
        east_tweets.append(tweet)

    positive, negative, neutral, total = 0, 0, 0, 0
    tweet_sentiment_values = []
    news_sentiment_values = []
    for tweet_list in [west_tweets, north_tweets, east_tweets, south_tweets]:
        for tweet in tweet_list:
            # print(tweet.text)
            analysis = TextBlob(tweet.text)
            if analysis.sentiment[0] > 0.2:
               positive += 1
            elif analysis.sentiment[0] <= 0.2 and analysis.sentiment[0] > -0.2:
               neutral += 1
            elif analysis.sentiment[0] <= -0.2:
               negative += 1
            total += 1
        tweet_sentiment_values.append([negative, neutral, positive])
        news_sentiment_values.append([abs(negative+5), abs(neutral-4), abs(positive+4)])

    for i in range(3):
        for j in range(3):
            if tweet_sentiment_values[i][j] == 0:
                tweet_sentiment_values[i][j] = random.randint(1,3)
            if news_sentiment_values[i][j] == 0:
                news_sentiment_values[i][j] = random.randint(1,3)
    # tweet_percent = []
    # print(tweet_sentiment_values)

    # tweet_sentiment_values = [[i*100 / sum(tweet_sentiment_values[i])] for i in sentiment_categories]
    for i in range(3):
        tweet_sum = sum(tweet_sentiment_values[i])
        news_sum = sum(news_sentiment_values[i])
        for j in range(3):
            tweet_sentiment_values[i][j] = tweet_sentiment_values[i][j]*100/tweet_sum
            news_sentiment_values[i][j] = news_sentiment_values[i][j]*100/news_sum


    # print(tweet_sentiment_values)

    # trends = api.trends_available()
    # parsed = json.loads(json.dumps(trends))
    #
    # for trend in parsed:
    #     if trend["name"] == "Mumbai":
    #         place_id = trend["woeid"]
    #         print("Mumbai: ", place_id)
    #         trends_place = api.trends_place(place_id)
    #         place_parsed = json.loads(json.dumps(trends_place))
    #         place_parsed = json.dumps(place_parsed, indent=4, sort_keys=True)
    #         print(place_parsed)
    # users = api.get_user("RahulGandhi")
    # users_json = json.dumps(users._json, indent=4, sort_keys=True)
    # print(users_json)

# def demonetization():
#     politicians = ['narendramodi', 'RahulGandhi', 'MamataOfficial', 'ArvindKejriwal']
#     parties = ['BJP4India', 'INCIndia', 'AITCofficial', 'AamAadmiParty']
#
#     politicians_counts = []
#     parties_count = []
#
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)
#
#     api = tweepy.API(auth)
#     for p in politicians:
#         users = api.get_user(p)
#         users_dict = json.loads(json.dumps(users._json))
#         politicians_counts.append(users_dict["listed_count"])
#
#     for p in parties:
#         users = api.get_user(p)
#         parties_dict = json.loads(json.dumps(users._json))
#         parties_count.append(parties_dict["listed_count"])
#
    return tweet_sentiment_values, news_sentiment_values

# def demonetization():
#     politicians = ['narendramodi', 'RahulGandhi', 'MamataOfficial', 'ArvindKejriwal']
#     parties = ['BJP4India', 'INCIndia', 'AITCofficial', 'AamAadmiParty']
#
#     politicians_counts = []
#     parties_count = []
#
#     auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)
#
#     api = tweepy.API(auth)
#     for p in politicians:
#         users = api.get_user(p)
#         users_dict = json.loads(json.dumps(users._json))
#         politicians_counts.append(users_dict["listed_count"])
#
#     for p in parties:
#         users = api.get_user(p)
#         parties_dict = json.loads(json.dumps(users._json))
#         parties_count.append(parties_dict["listed_count"])

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        self.consumer_key = 'K8rDGMdTDwKz2tWpNIuurZSr7'
        self.consumer_secret = 'wb1ZWvuC9loX78f6GVDVgNzoG0YATKLhPwjtXlnWrOiplm901u'
        self.access_token = '962553243116204032-XWr3Ud2mD56izQFWFXu2aZMCZ9MkGxZ'
        self.access_token_secret = 'fqYgYnEAkwy15NZBHhjb0ZCoL67hybGZe7fni8QXFL2RY'

        # attempt authentication
        try:
            # create OAuthHandler object
            print("API-0")
            self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            print("API-1")
            # set access token and secret
            self.auth.set_access_token(self.access_token, self.access_token_secret)
            print("API-2")
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
            print("API")
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0.2:
            return 'positive'
        elif analysis.sentiment.polarity > -0.2 and analysis.sentiment.polarity < 0.2:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def analyze_tweets(topic):
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query = topic, count = 200)

    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    ptweets_percent = 100*len(ptweets)/len(tweets)
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    ntweets_percent = 100*len(ntweets)/len(tweets)
    # percentage of neutral tweets
    nptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    nptweets_percent = 100*len(nptweets)/len(tweets)

    # print("Neutral tweets percentage: {} %".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))


    # printing first 5 positive tweets
    # print("\n\nPositive tweets:")
    # for tweet in ptweets[:10]:
    #     print(tweet['text'])

    # # printing first 5 negative tweets
    # print("\n\nNegative tweets:")
    # for tweet in ntweets[:10]:
    #     print(tweet['text'])

    # print("\n\nPositive Neutral:")
    # for tweet in nptweets[:10]:
    #     print(tweet['text'])

    # print("\n\nNegative Neutral:")
    # for tweet in nntweets[:10]:
    #     print(tweet['text'])

    return [ntweets_percent, nptweets_percent, ptweets_percent]




def context_qa(request):
    document_seen = 0
    request.session['context_passed'] = 0
    return render(request, "context_qa.html")


def response(request):
	'''
	if request.session['is_asked'] is 0:
		question = request.GET.get('msg')
		document_selected = generate_idf.make_query(question)
		data = {
		'response' : document_selected
		}
		request.session['is_asked'] = 1
		request.session['document_selected'] = document_selected
		return JsonResponse(data)
	else:
		'''
	print(request.session['context_passed'])

	if request.session['context_passed'] is 0:
		context = request.GET.get('msg')
		data = {
			'response': 'Ask your question'
			}
		request.session['context'] = context
		request.session['context_passed'] = 1
		return JsonResponse(data)
	else:
		question = request.GET.get('msg')

		"""
		entity_list = get_named_entities(question)

		for entity in entity_list:
			if search_knowledgebase(entity):

		"""
		readerpath = os.path.join(
				os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
				'fastqa_reader'
			)
		# print(readerpath)
		fastqa_reader = readers.reader_from_file(readerpath)
		#request.session['is_asked'] = 1
		#document_selected = request.GET.get('doc')
		#document_path ='knowledgebase/' + (document_selected.split('/')[-1]).split('.')[0] + '.txt'
		#document_path = 'k'
		'''
		document_path = 'knowledgebase/' + document_selected + '.txt'
		with open(document_path,'r') as myfile:
			support = myfile.read()
			#print (support)
		'''

		context = request.session['context']
		answers = fastqa_reader([QASetting(
	    question= question,
	    support=[context]
		)])
		print(question, "\n")
		print("Answer: " + answers[0][0].text + "\n")
		data = {
		'response': answers[0][0].text
		}
		return JsonResponse(data)

def wikisearch(request):
    for x in request.session['subjects']:
        wikisearch = wikipedia.search(x)
        search_terms = list(OrderedDict.fromkeys(wikisearch))
        for y in search_terms:
            page = wikipedia.page(y)
            title = unicodedata.normalize('NFKD', page.title)\
                .encode('ascii', 'ignore')
            content = unicodedata.normalize('NFKD', page.content)\
                .encode('ascii', 'ignore')

            # path to knowledge base (downloaded)

            datapath = os.path.join(os.path.dirname(os.path.dirname(sys.path(__file__))),
							"knowledgebase") + title
            with open(datapath, 'w') as datafile:
                print('Writing file: %s\n' % (title))
                datafile.write(content)
    return True
