# DS
Internship Assignment
# News Aggregator

## Project Overview
This News Aggregator fetches news articles from various RSS feeds, stores them in a PostgreSQL database, and periodically updates the database using Celery. It's designed to help users keep up-to-date with news from multiple sources in a centralized manner.

## Installation Instructions

### Prerequisites
- Python 3.8 or newer
- PostgreSQL
- RabbitMQ

### Setup Environment
1. **Clone the repository:**
   ```bash
   git clone https://your-repository-url.git
   cd news_aggregator

2. Set up a Python virtual environment and activate it:
  python -m venv venv
  .\venv\Scripts\activate

3. Install required Python packages:

4. Configure Database
Ensure PostgreSQL is running and create a database named newsdb:

5. Modify the database connection string in models.py if different from the default setup:
  engine = create_engine('postgresql://postgres:yourpassword@localhost/newsdb')

6.Start Celery Worker
Run the Celery worker to handle background tasks:
  celery -A app worker --loglevel=info


Code snippets- 
**app.py (fetching and storing articles)**

def fetch_and_store_articles():
    session = Session()
    feeds = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        # Additional feeds
    ]
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if not session.query(Article).filter_by(url=entry.link).first():
                article = Article(
                    title=entry.title,
                    content=entry.summary if 'summary' in entry else 'No summary available',
                    pub_date=datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.now(),
                    url=entry.link
                )
                session.add(article)
    session.commit()
    session.close()


   **Database Models (models.py)**

   Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    pub_date = Column(DateTime)
    url = Column(String(255), unique=True)

engine = create_engine(''postgresql://postgres:yourpassword@localhost/newsdb')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


. **Scheduling Tasks with Celery (app.py)**

app = Celery('tasks', broker='pyamqp://guest@localhost//')

app.conf.beat_schedule = {
    'fetch-and-store-articles-every-30-minutes': {
        'task': 'app.fetch_and_store_articles',
        'schedule': crontab(minute='*/30')
    }
}

@app.task
def fetch_and_store_articles_task():
    fetch_and_store_articles()
