# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_chop= latest_date[0].split("-")
    start_year= int(date_chop[0])-1
    start_date= str(start_year)+"-"+date_chop[1]+"-"+date_chop[2]
    
    
    # Query for the date and precipitation for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip)



@app.route("/api/v1.0/stations")
def station():
    list_stations= session.query(Station.station).all()
    session.close()
    list_of_stations = list(np.ravel(list_stations)) 
    return jsonify(list_of_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_chop= latest_date[0].split("-")
    start_year= int(date_chop[0])-1
    start_date= str(start_year)+"-"+date_chop[1]+"-"+date_chop[2]

    # Calculate the most active station
    traffic = [Measurement.station, 
       func.count(Measurement.station)]
    active_stations = session.query(*traffic).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active = active_stations[0][0]

    # Query the dates and temperature observations of the most active station for the last year of data
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= start_date).\
        group_by(Measurement.date).order_by(Measurement.date).all()

    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps)



@app.route("/api/v1.0/<start>")
def start_date(start):
    sl = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sl).filter(Measurement.date >= start).all()
    temps = list(np.ravel(results))
    return jsonify(temps)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    sl = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sl).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


# Create our session (link) from Python to the DB
if __name__ == '__main__':
    app.run(debug=True)