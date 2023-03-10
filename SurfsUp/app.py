#import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from flask import Flask, jsonify

#database setup
database_path = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

#Reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(autoload_with=engine)

#Save references to the table
m = Base.classes.measurement
s = Base.classes.station

#flask setup
app = Flask(__name__)

#Available routes
@app.route("/")
def index():
    """List all available api routes"""
    return(
        f"Welcome to the Climate Analysis API:<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Define when user hits route
@app.route("/api/v1.0/precipitation")
def precipation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """precipitation analysis - retrieving only the last 12 months of data)"""
    # Query data
    data = session.query(m.date,m.prcp).all()

    session.close()

    # Create a dictionary from the data and append to a new list

    prcp_analysis = []
    for date, prcp in data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_analysis.append(prcp_dict)

    return jsonify(prcp_analysis)




@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the dataset"""
    # Query all stations
    results = session.query(s.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the dates and temperature observations of the most-active station for the previous year of data"""
    # Query the dates and temperature
    tobs_results = session.query(m.tobs).filter(m.station == 'USC00519281').filter(m.date >= '2016-08-23').all()
    dates_results = session.query(m.date).filter(m.station == 'USC00519281').filter(m.date >= '2016-08-23').all()

    session.close()

    tobs_results = list(np.ravel(tobs_results))
    dates_results = list(np.ravel(dates_results))

    return jsonify(tobs_results, dates_results)


import datetime as dt
@app.route("/api/v1.0/temp/<start>")
def start(start=None):
    start = dt.datetime.strptime(start, "%m%d%Y")
  
    session = Session(engine)

    """list of the minimum temperature, the average temperature,\
          and the maximum temperature for a specified start"""
    TMIN = session.query(func.min(m.tobs)).filter(m.date >= start).all()
    TAVG = session.query(func.avg(m.tobs)).filter(m.date >= start).all()
    TMAX = session.query(func.max(m.tobs)).filter(m.date >= start).all()
    
    session.close()

    TMIN = list(np.ravel(TMIN))
    TMAX = list(np.ravel(TMAX))
    TAVG = list(np.ravel(TAVG))

    return jsonify(TMIN, TMAX,TAVG)


@app.route("/api/v1.0/temp/<start>/<end>")
def temp(start,end):
    # Create our session (link) from Python to the DB
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    session = Session(engine)

    """Return a list of the minimum temperature, the average temperature, \
        and the maximum temperature for a specified start or start-end range."""
    # Query passengers based on start and end dates
    TMIN = session.query(func.min(m.tobs)).filter(m.date >= start).filter(m.date < end).all()
    TMAX = session.query(func.max(m.tobs)).filter(m.date >= start).filter(m.date < end).all()
    TAVG = session.query(func.avg(m.tobs)).filter(m.date >= start).filter(m.date < end).all()

    session.close()

    TMIN = list(np.ravel(TMIN))
    TMAX = list(np.ravel(TMAX))
    TAVG = list(np.ravel(TAVG))


    return jsonify(TMIN, TMAX,TAVG)


if __name__ == "__main__":
    app.run(debug=True)