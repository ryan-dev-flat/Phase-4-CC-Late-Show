from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Episode(db.Model, SerializerMixin):
    __tablename__ = 'episodes'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    appearances = db.relationship('Appearance', back_populates='episode')
    guests = association_proxy('appearances', 'guest')

    serialize_rules = ('-appearances.episode',)

    def __repr__(self):
        return f'<Episode {self.id} {self.date} {self.number}>'




class Appearance(db.Model, SerializerMixin):
    __tablename__ = 'appearances'

    id = db.Column(db.Integer, primary_key=True)

    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guests.id'))

    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    episode = db.relationship('Episode', back_populates='appearances')
    guest = db.relationship('Guest', back_populates='appearances')

    @validates('rating')
    def validate_rating(self, key, app_rating):
        if not (1 <= app_rating <= 5):
            raise ValueError('400: Validation error.')
        return app_rating

    serialize_rules = ('-episode.appearances', '-guest.appearances')



    def __repr__(self):
        return f'<Appearance {self.id} {self.rating} {self.episode_id} {self.guest_id} >'

class Guest(db.Model, SerializerMixin):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    occupation =  db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    appearances = db.relationship('Appearance', back_populates='guest')
    episodes = association_proxy('appearances', 'episode')

    serialize_rules=('-appearances.guest',)

    def __repr__(self):
        return f'<Guest {self.id} {self.name} {self.occupation}>'

