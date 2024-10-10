from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    pub_date = Column(DateTime)
    url = Column(String(255), unique=True)
    category = Column(String(50), default='Others')

# Setup the database connection
engine = create_engine('postgresql://postgres:abc123@localhost/newsdb')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
