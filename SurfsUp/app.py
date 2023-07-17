# Import the dependencies.
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/passengers<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
    #Convert the query results from the precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Starting from the most recent data point in the database.
    last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    latest_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year = dt.date(latest_date.year - 1, latest_date.month, latest_date.day)
    one_year
    # # Perform a query to retrieve the data and precipitation scores
    sel = [Measurements.date, Measurements.prcp]
    results = session.query(*sel).filter(Measurements.date >= one_year).all()
    results
