#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask.sessions import SessionInterface
from sqlalchemy.orm import relation, relationship, session
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import CRITICAL, Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db,Venue,Artist,Show
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venue=Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
  artist=Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
  return render_template('pages/home.html',venues=venue,artists=artist)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  places=Venue.query.distinct(Venue.city, Venue.state).all()
  data=[]
  for p in places:
    venue=Venue.query.filter(Venue.city==p.city,Venue.state==p.state)
    place={}
    place={
      "city":p.city,
      "state":p.state,
      }
    veunes=[]
    for v in venue:
      if v.city==p.city and v.state==p.state:
        veunes.append({
          "id":v.id,
          "name":v.name})  
      else:
        continue
    place["venues"]=veunes   
    data.append(place)    
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_query=db.session.query(Venue.id,Venue.name).filter(Venue.name.ilike('%'+request.form['search_term']+'%'))
  data=[]
  for s in search_query:
    data.append({
      "id": s.id,
      "name": s.name,
      "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==s.id).filter(Show.show_date >= datetime.now()).count()
    }) 
  response={
    "count":search_query.count(),
    "data": data
  }  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  show_time=db.session.query(Artist.id,Artist.name,Artist.image_link,Show.show_date).\
    join(Show).filter(Show.venue_id==venue_id)
  upcoming_shows=[]
  past_show=[]
  past_shows_count=0
  upcoming_shows_count=0
  for show in show_time:
    temp={
      "artist_id":show.id ,
      "artist_name":show.name ,
      "artist_image_link": show.image_link ,
      "start_time":show.show_date.strftime("%d/%m/%Y, %H:%M")
    }
    if show.show_date >= datetime.now():
      upcoming_shows.append(temp)
      upcoming_shows_count+=1 
    else:
      past_show.append(temp)
      past_shows_count+=1
        
  data={
    "id":venue.id ,
    "name": venue.name ,
    "genres":venue.genres,
    "address":venue.address ,
    "city":venue.city ,
    "state":venue.state,
    "phone": venue.phone,
    "website":venue.website,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.seeking_talent ,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_show,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form=VenueForm()
  try:
    venue=Venue(name=form.name.data,city=form.city.data,state=form.state.data,address=form.address.data,
                phone=form.phone.data,genres=form.genres.data,image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,website=form.website_link.data,
                seeking_talent=form.seeking_talent.data,seeking_description=form.seeking_description.data)
    db.session.add(venue)
    db.session.commit()
     # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occurred. Venue ' + form.data.name + ' could not be listed.')
  finally:  
    db.session.close()
  
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue=Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:    
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=db.session.query(Artist.id,Artist.name).all()
  datas=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_query=db.session.query(Artist.id,Artist.name).filter(Artist.name.ilike('%'+request.form['search_term']+'%'))
  data=[]
  for s in search_query:
    data.append({
      "id": s.id,
      "name": s.name,
      "num_upcoming_shows": db.session.query(Show).filter(Show.artist_id==s.id).filter(Show.show_date >= datetime.now()).count()
    }) 
  response={
    "count":search_query.count(),
    "data": data
  }  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.get(artist_id)
  show_time=db.session.query(Venue.id,Venue.name,Venue.image_link,Show.show_date).\
    join(Venue).filter(Show.artist_id==artist_id)
  upcoming_shows=[]
  past_show=[]
  past_shows_count=0
  upcoming_shows_count=0
  for show in show_time:
    temp={
      "venue_id":show.id ,
      "venue_name":show.name ,
      "venue_image_link": show.image_link ,
      "start_time":show.show_date.strftime("%d/%m/%Y, %H:%M")
    }
    if show.show_date >= datetime.now():
      upcoming_shows.append(temp)
      upcoming_shows_count+=1 
    else:
      past_show.append(temp)
      past_shows_count+=1
        
  data={
    "id":artist.id ,
    "name": artist.name ,
    "genres":artist.genres,
    "city":artist.city ,
    "state":artist.state,
    "phone": artist.phone,
    "website":artist.website,
    "facebook_link":artist.facebook_link,
    "seeking_venue":artist.seeking_venues ,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_show,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form=ArtistForm()
  try:
    artist=Artist.query.get(artist_id)
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.image_link=form.image_link.data
    artist.facebook_link=form.facebook_link.data
    artist.website=form.website_link.data
    artist.seeking_venues=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Artist' + request.form['name'] + ' information was successfully updated!')
  except:
    flash('An error occurred. Artist ' + form.name.data + ' information could not be update.')
    db.session.rollback()
  finally:
    db.session.close()  

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form=VenueForm()
  try:
    venue=Venue.query.get(venue_id)
    venue.name=form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.address=form.address.data
    venue.phone=form.phone.data
    venue.genres=form.genres.data
    venue.image_link=form.image_link.data,
    venue.facebook_link=form.facebook_link.data
    venue.website=form.website_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form=ArtistForm()
  try:
    new_artist=Artist(name=form.name.data,city=form.city.data,state=form.state.data,phone=form.phone.data,
                      genres=form.genres.data,image_link=form.image_link.data,facebook_link=form.facebook_link.data,
                      website=form.website_link.data,seeking_venues=form.seeking_venue.data,seeking_description=form.seeking_description.data)
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:    
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
   return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows=db.session.query(Show.venue_id,Venue.name.label('venue_name'),
                   Show.artist_id,Artist.name.label('artist_name'),Artist.image_link,Show.show_date).\
                     join(Artist,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).all()
  data=[]
  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name":show.venue_name,
    "artist_id": show.artist_id,
    "artist_name":show.artist_name,
    "artist_image_link": show.image_link,
    "start_time":show.show_date.strftime("%d/%m/%Y, %H:%M")
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
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm()
  try:
    new_show=Show(venue_id=form.venue_id.data,artist_id=form.artist_id.data,show_date=form.start_time.data)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:    
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
