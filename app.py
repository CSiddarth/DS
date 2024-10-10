import feedparser
from datetime import datetime
from models import Article, Session

def fetch_and_store_articles():
    session = Session()
    feeds = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
        # Add more feeds as needed
    ]

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.title if 'title' in entry else 'No Title'
            link = entry.link if 'link' in entry else 'No Link'
            content = entry.summary if 'summary' in entry else 'No summary available'
            print(f"Title: {title}, Link: {link}, Content: {content[:100]}")
            # Handle pubDate with checking if it's present and correctly formatted
            if 'published_parsed' in entry:
                pub_date = datetime(*entry.published_parsed[:6])
            else:
                pub_date = datetime.now()  # Use current time if publication date is not available
            
            # Some feeds use 'summary', others 'description', or even 'content'
            content = entry.summary if 'summary' in entry else (entry.description if 'description' in entry else 'No Content Available')

            # Check if article already exists to prevent duplicates
            if not session.query(Article).filter_by(url=link).first():
                article = Article(
                    title=title,
                    content=content,
                    pub_date=pub_date,
                    url=link
                )
                session.add(article)

                
    
    session.commit()
    session.close()
    print("Articles fetched and stored successfully.")

fetch_and_store_articles()

from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='pyamqp://guest@localhost//')

# Schedule
app.conf.beat_schedule = {
    'fetch-and-store-articles-every-1-minute': {
        'task': 'app.fetch_and_store_articles',
        'schedule': crontab(minute='*/1'),  # Executes every 30 minutes
    }
}

@app.task
def fetch_and_store_articles():
    # Your fetching and storing logic here
    print("Fetching and storing articles...")
