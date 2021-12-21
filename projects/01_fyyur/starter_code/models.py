from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def __init__(self, name, city, state, address, phone, genres, image_link,
                 facebook_link, website, seeking_talent, seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description
        }


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def __init__(self, name, city, state, address, phone, genres, image_link,
                 facebook_link, website, seeking_venues, seeking_description):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_venues = seeking_venues
        self.seeking_description = seeking_description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venues": self.seeking_venues,
            "seeking_description": self.seeking_description
        }


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer,
                         db.ForeignKey('venue.id', ondelete='CASCADE'),
                         nullable=False)
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('artist.id', ondelete='CASCADE'),
                          nullable=False)
    show_date = db.Column(db.DateTime, nullable=False)
    # relationships
    Venue_r = db.relationship('Venue',
                              backref=db.backref('shows', cascade='all, delete'))
    artist_r = db.relationship('Artist',
                               backref=db.backref('shows', cascade='all, delete'))

    def __init__(self, venue_id, artist_id, show_date):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.show_date = show_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "venue_id": self.venue_id,
            "artist_id": self.artist_id,
            "show_date": self.show_date
        }
