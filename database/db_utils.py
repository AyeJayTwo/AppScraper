from datetime import datetime, date
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from .models import RetailerRating, init_db

def get_session():
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()

def get_todays_rating(retailer_name: str) -> dict:
    """
    Get today's rating for a retailer if it exists.
    Returns None if no rating exists for today.
    """
    session = get_session()
    try:
        today = date.today()
        rating = session.query(RetailerRating).filter(
            and_(
                RetailerRating.retailer_name == retailer_name,
                RetailerRating.date >= today
            )
        ).first()
        return rating.to_dict() if rating else None
    finally:
        session.close()

def save_rating(rating_data: dict) -> None:
    """
    Save a retailer's rating data to the database.
    """
    session = get_session()
    try:
        rating = RetailerRating(**rating_data)
        session.add(rating)
        session.commit()
    finally:
        session.close()

def get_all_ratings() -> list:
    """
    Get all ratings for all retailers.
    """
    session = get_session()
    try:
        ratings = session.query(RetailerRating).order_by(RetailerRating.date.desc()).all()
        return [rating.to_dict() for rating in ratings]
    finally:
        session.close()

def get_all_retailers():
    """
    Get the latest entry for each retailer.
    """
    session = get_session()
    try:
        # Get the latest entry for each retailer
        latest_ratings = session.query(RetailerRating).distinct(RetailerRating.retailer_name).all()
        return [{
            'retailer_name': r.retailer_name,
            'ios_url': r.ios_url,
            'android_url': r.android_url
        } for r in latest_ratings]
    finally:
        session.close()

def update_retailer(old_name, new_data):
    """
    Update all entries for a retailer with new data.
    """
    session = get_session()
    try:
        # Update all entries for this retailer
        ratings = session.query(RetailerRating).filter(
            RetailerRating.retailer_name == old_name
        ).all()
        
        for rating in ratings:
            for key, value in new_data.items():
                setattr(rating, key, value)
        
        session.commit()
    finally:
        session.close()

def delete_retailer(retailer_name):
    """
    Delete all entries for a retailer.
    """
    session = get_session()
    try:
        # Delete all entries for this retailer
        session.query(RetailerRating).filter(
            RetailerRating.retailer_name == retailer_name
        ).delete()
        session.commit()
    finally:
        session.close() 