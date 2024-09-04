import pytest

from app import app
from models import db, Appearance

class TestApp:
    '''Models in app.py'''
    
    def test_appearance_validates_rating(self):
        '''requires appearance ratings to be integers between 1 and 5, inclusive.'''
        
        with app.app_context():
            Appearance.query.delete()
            db.session.commit()

            with pytest.raises(ValueError):
                Appearance(rating=0)
            
            with pytest.raises(ValueError):
                Appearance(rating=6)
