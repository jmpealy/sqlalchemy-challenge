# Import the dependencies.
import os
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, exc
from sqlalchemy import func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation Data (last 12 months): /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature obervations (last 12 months): /api/v1.0/tobs<br/>"
        f"Temperature obervation stats from start date (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature obervation stats from start date to end dates (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
    #Convert the query results from the precipitation analysis (one year's worth of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database.
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    latest_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year = dt.date(latest_date.year - 1, latest_date.month, latest_date.day)
 
    # # Perform a query to retrieve the data and precipitation scores
    sel = [Measurements.date, Measurements.prcp]
    results = session.query(*sel).filter(Measurements.date >= one_year).all()

    #Create a dictionary of precipitation results
    precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Precipitation'] = prcp
        precip.append(prcp_dict)
    
    return jsonify(precip)

    #Create a query of all the station data
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    #Organize the station data into a dictionary
    stations = []
    for station, name, lat, lon, elev in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = elev
        stations.append(station_dict)

    #Return a JSON list of all the stations
    return jsonify(stations)

    #Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurements.date, Measurements.tobs]
    queryresult = session.query(*sel).filter(Measurements.date >= querydate).all()
    session.close()

    #Organize the data into a dictionary
    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    #Return a JSON list of temperature observations for the previous year.
    return jsonify(tobsall)

    #Create a query returning TOBS stats for a period starting from a certain date until the end of the dataset
@app.route('/api/v1.0/<start>')
def get_tobs_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).all()
    session.close()

    #Organize the data into a dictionary
    tobsall = []
    for min, avg, max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Average"] = avg
        tobsall.append(tobs_dict)

    #Return a JSON list of the TOBS stats for a specified start range
    return jsonify(tobsall)

    #Create a query returning TOBS stats for a period between two defined dates
@app.route('/api/v1.0/<start>/<stop>')
def get_tobs_start_stop(start, stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).filter(Measurements.date <= stop).all()
    session.close()

    #Organize the data into a dictionary
    tobsall = []
    for min, avg, max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Average"] = avg
        tobsall.append(tobs_dict)

    #Return a JSON list of the TOBS stats for a specified start-end range
    return jsonify(tobsall)

if __name__=='__main__':
    app.run(debug=True)