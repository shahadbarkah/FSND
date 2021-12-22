# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
from operator import add
import dateutil.parser
from flask.sessions import SessionInterface
from sqlalchemy.orm import relation, relationship, session
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import CRITICAL, Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format = "EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format = "EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
  venue = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
  artist = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
  return render_template('pages/home.html', venues=venue, artists=artist)


#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
  # List venue data based on city and state
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []
  for p in places:
    venue = Venue.query.filter(Venue.city==p.city, Venue.state==p.state)
    place = {}
    place = {
        "city": p.city,
        "state": p.state,
        }
    veunes = []
    for v in venue:
      if v.city == p.city and v.state == p.state:
        veunes.append({
          "id": v.id,
          "name": v.name})
      else:
        continue
    place["venues"] = veunes
    data.append(place)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Implement search on artists with partial string search. It is case-insensitive.
  search_term = request.form['search_term']
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id)\
                                      .filter(Show.show_date >= datetime.now())\
                                      .count()
    })
  response = {
    "count": len(venues),
    "data": data
  }  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  show_time = Artist.query.with_entities(Artist.id,Artist.name,Artist.image_link,Show.show_date)\
                    .join(Show).filter(Show.venue_id==venue_id)
  upcoming_shows = []
  past_show = []
  
  for show in show_time:
    temp = {
      "artist_id": show.id ,
      "artist_name": show.name ,
      "artist_image_link": show.image_link ,
      "start_time": show.show_date.strftime("%d/%m/%Y, %H:%M")
    }

    if show.show_date >= datetime.now():
      upcoming_shows.append(temp)
    elif show.show_date < datetime.now():
      past_show.append(temp)
        
  data = venue.format()
  data["past_shows"] = past_show
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_show)
  data["upcoming_shows_count"] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Insert form data as a new Venue record in the db
  form = VenueForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data,
  facebook_link = form.facebook_link.data
  website = form.website_link.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data
  try:
    venue = Venue(name, city, state, address, phone, genres,
                  image_link, facebook_link, website, 
                  seeking_talent, seeking_description
                  )
    venue.insert()
     # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except:
  #  on unsuccessful db insert, flash an error.
    db.session.rollback()
    flash('An error occurred. Venue ' + name+ ' could not be listed.')
  finally:  
    db.session.close()
  
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # eEndpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record.

  try:
    venue = Venue.query.get(venue_id)
    venue.delete()

  except:
    db.session.rollback()

  finally:  
    db.session.close()

  # Redirect the user to the homepage
  return redirect(url_for('index')) 


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Implement search on artists with partial string search.It is case-insensitive.
  search_term = request.form['search_term']
  artists = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%'))
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id==artist.id).filter(Show.show_date >= datetime.now()).count()
    }) 
  response = {
    "count":artists.count(),
    "data": data
  }  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  venues = Venue.query.with_entities(Venue.id,Venue.name,Venue.image_link,Show.show_date)\
                   .join(Show).filter(Show.artist_id==artist_id)
  upcoming_shows = []
  past_show = []

  for venue in venues:
    temp = {
      "venue_id": venue.id ,
      "venue_name": venue.name ,
      "venue_image_link": venue.image_link ,
      "start_time": venue.show_date.strftime("%d/%m/%Y, %H:%M")
      }
    if venue.show_date >= datetime.now():
      upcoming_shows.append(temp)

    elif venue.show_date < datetime.now():
      past_show.append(temp)

  data = artist.format()
  data["past_shows"] = past_show
  data["upcoming_shows"] = upcoming_shows
  data["past_shows_count"] = len(past_show)
  data["upcoming_shows_count"] = len(upcoming_shows)
   
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.seeking_venues = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.update()
    flash('Artist ' + form.name.data + ' information was successfully updated!')
  except:
    flash('An error occurred. Artist ' + form.name.data + ' information could not be update.')
    db.session.rollback()
  finally:
    db.session.close()  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data,
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.update()
    flash('Venue ' + form.data.name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.data.name + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.state.data
  image_link = form.state.data
  genres = form.genres.data
  facebook_link = form.facebook_link.data
  website = form.website_link.data
  seeking_venues = form.seeking_venue.data
  seeking_description = form.seeking_description.data

  try:
    artist=Artist(name, city, state, phone, genres,
                  image_link, facebook_link, website,
                  seeking_venues, seeking_description)
    artist.insert()
    flash('Artist ' + form.name.data + ' was successfully listed!')

  except:
    # On unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')

  finally:
   return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.with_entities(Show.venue_id, Venue.name.label('venue_name'),
                                  Show.artist_id, Artist.name.label('artist_name'),
                                  Artist.image_link.label('artist_image_link'), Show.show_date)\
                .join(Artist, Artist.id==Show.artist_id).join(Venue, Venue.id==Show.venue_id).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.show_date.strftime("%d/%m/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db
  form = ShowForm(request.form)
  venue_id=form.venue_id.data
  artist_id=form.artist_id.data
  show_date=form.start_time.data
  try:
    show = Show(venue_id, artist_id, show_date)
    show.insert
    # On successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # On unsuccessful db insert, flash an error
    flash('An error occurred. Show could not be listed.')
  finally:    
    db.session.close()

  return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
