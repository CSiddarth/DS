import feedparser
from datetime import datetime
from models import Article, Session
import csv
from celery import Celery
from celery.schedules import crontab

# Define the Celery app
app = Celery('tasks', broker='pyamqp://guest@localhost//')

def fetch_and_store_articles():
    """
    Fetches articles from specified RSS feeds, stores new entries in the database,
    and exports newly fetched articles to a CSV file.
    """
    session = Session()
    feeds = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
    ]

    articles_to_export = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.title if 'title' in entry else 'No Title'
            link = entry.link if 'link' in entry else 'No Link'
            content = entry.summary if 'summary' in entry else 'No summary available'

            if 'published_parsed' in entry:
                pub_date = datetime(*entry.published_parsed[:6])
            else:
                pub_date = datetime.now()

            if not session.query(Article).filter_by(url=link).first():
                article = Article(
                    title=title,
                    content=content,
                    pub_date=pub_date,
                    url=link
                )
                session.add(article)
                articles_to_export.append([title, content, pub_date.strftime("%Y-%m-%d %H:%M:%S"), link])

    session.commit()
    session.close()

    # Export to CSV after storing in database
    if articles_to_export:
        export_to_csv(articles_to_export)
    print("Articles fetched and stored successfully.")

def export_to_csv(articles):
    """
    Exports a list of articles to a CSV file.
    """
    filename = 'exported_articles.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Content', 'Publication Date', 'URL'])
        writer.writerows(articles)
    print(f"Data exported to {filename} successfully.")

# Celery task
@app.task
def scheduled_fetch_and_store_articles():
    print("Scheduled task: Fetching and storing articles...")
    fetch_and_store_articles()

# Celery beat schedule
app.conf.beat_schedule = {
    'fetch-and-store-articles-every-1-minute': {
        'task': 'app.scheduled_fetch_and_store_articles',
        'schedule': crontab(minute='*/1'),  # Adjust as necessary
    }
}

if __name__ == '__main__':
    fetch_and_store_articles()
