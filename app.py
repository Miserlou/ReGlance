from datetime import datetime
from email.Utils import formatdate
from flask import Flask, Response, jsonify
from feeds import FEEDS
from maya import MayaDT
from time import mktime
from thefuture import Future

import feedparser
import json
import re
import time
import uuid

##
# AWS
##

##
# Flask
##

app = Flask(__name__)

@app.route('/')
def hello():
    """ """
    return "Please supply a feed name!"

@app.route('/record/', methods=["POST"])
def record():
    """ Record a Glance. """
    return "Recorded!"

@app.route('/popular/')
def popular():
    """ Returns a feed of the most read articles over the past 24 hours. """
    return app.response_class(
        response='[]',
        status=200,
        mimetype='application/json'
    )

@app.route('/recent/')
def recent():
    """ Returns a feed of the most recently read articles. """
    return app.response_class(
        response='[]',
        status=200,
        mimetype='application/json'
    )

@app.route('/<feed_name>')
def feed(feed_name):
    """
    Find this feed name, parse those feeds in parallel and return our master-feed.

    Master-feed format:
        {
          "title": "The Week's Coolest Space Photos",
          "description": "Every day satellites are zooming through space, snapping incredible pictures of Earth, the solar system and outer space. Here are the highlights from this week.",
          "link": "http://digg.com/2017/best-space-images-9-16",
          "guid": "http://on.digg.com/2vYKaux",
          "pubDate": "Fri, 15 Sep 2017 19:25:15 +0000"
        }
    pubDate is RFC 2822.

    """
    if not FEEDS.has_key(feed_name):
        return "We don't have that feed!", 400

    entries = parse_feeds(FEEDS[feed_name])
    dumped = json.dumps(entries, default=convert_time)

    return app.response_class(
        response=dumped,
        status=200,
        mimetype='application/json'
    )

##
# Parsing
##

def parse_feeds(feed_list):

    # pull down all feeds
    future_calls = [Future(feedparser.parse, rss_url) for rss_url in feed_list]
    # block until they are all in
    feeds = [future_obj() for future_obj in future_calls]

    entries = []
    for feed in feeds:
        for item in reversed(feed["items"]):
            entry_item = [{
              "title": item['title'],
              "description": clean_html(item.get('summary','')).strip()[:200],
              "link": item['link'],
              "guid": str(uuid.uuid4()),
              "pubDate": item.get('published_parsed', None)
            }]
            entries.extend(entry_item)

    sorted_entries = sorted(entries, key=lambda entry: entry.get("pubDate", None))
    sorted_entries.reverse() # for most recent entries first

    return sorted_entries

##
# Util
##

def convert_time(o):
    """ Takes a struct_time, returns an RFC 2822 """
    if isinstance(o, time.struct_time):
        dt = datetime.fromtimestamp(mktime(o))
        maya_dt = MayaDT.from_datetime(dt)
        return maya_dt.rfc2822()

def clean_html(raw_html):
    """ via https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
