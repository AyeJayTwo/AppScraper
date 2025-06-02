from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RetailerRating(Base):
    __tablename__ = 'retailer_ratings'
    
    id = Column(Integer, primary_key=True)
    retailer_name = Column(String)
    ios_url = Column(String)
    android_url = Column(String)
    ios_score = Column(Float)
    ios_reviews = Column(Integer)
    android_score = Column(Float)
    android_reviews = Column(Integer)
    weighted_average = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'retailer_name': self.retailer_name,
            'ios_url': self.ios_url,
            'android_url': self.android_url,
            'ios_score': self.ios_score,
            'ios_reviews': self.ios_reviews,
            'android_score': self.android_score,
            'android_reviews': self.android_reviews,
            'weighted_average': self.weighted_average,
            'date': self.date
        }

def init_db():
    engine = create_engine('sqlite:///retailer_ratings.db')
    Base.metadata.create_all(engine)
    return engine 