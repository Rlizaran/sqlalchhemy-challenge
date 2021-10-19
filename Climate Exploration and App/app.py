import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from sqlalchemy.sql.expression import and_

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    print("Request received for 'Home' page....")
    return (
        f"<h1>Available Routes for Hawaii weather API:</h1>"
        f"/api/v1.0/precipitation <br>"
        f"/api/v1.0/stations <br>"
        f"/api/v1.0/tobs <br><br>"
        f"<h3>For the following routes, use date format: <strong>YYYY-MM-DD</strong></h3>"
        f"/api/v1.0/&ltstart_date&gt <br>"
        f"/api/v1.0/&ltstart_date&gt/&ltend_date&gt"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Qery the DataBase for date and precipitation base on
        the last day present on the DataBase"""
    print("Request received for 'Precipitation' page....")

    # Recall most_recent_date_def function to get last day on the Measurement table
    query_date_1year = most_recent_date_def()
    print(f"precitpitation route: {query_date_1year}")

    # Extract data 1 year before last day entered on Measurement Table
    session = Session(engine)
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date_1year).order_by(Measurement.date).all()
    session.close()

    # Extract data to be jsonify
    result = []
    for date, prcp in prcp_data:
        result_dict = {}
        result_dict['Date'] = date
        result_dict['Precipitation'] = prcp
        result.append(result_dict)
    
    # Return json
    return jsonify(result)

    
@app.route("/api/v1.0/stations")
def stations():
    """Query data for stations on the DataBase"""

    print("Rquest received for 'Stations' page...")

    # Start session
    session = Session(engine)

    # Query data for stations
    result = session.query(Station.station, Station.station).all()

    # Extract data to be jsonify
    result_list = []
    for station, col in result:
        result_list.append(station)

    # End session
    session.close()

    # Return json
    return jsonify(result_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Query data for dates and temperatures observations 
     of the most active station for the last year of data """

    print("Request received for 'Tobs' page...")
    
    # Calculate the date one year from the last date in data set. Use function most_recent_date_def()
    query_date_1year = most_recent_date_def()
    print(f"tobs route: {query_date_1year}")

    session = Session(engine)
     #List the stations and the counts in descending order.
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    most_active_stations = active_stations[0][0]

    # datas and temp obs on most active station for the last year
    tmp_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date_1year).\
                filter(Measurement.station == most_active_stations).all()
    
    # End session
    session.close()

    # Extract data to be jsonify
    result_list = []

    for date, tobs in tmp_data:
        result_dict = {}
        result_dict['Date'] = date
        result_dict['Temperature'] = tobs
        result_list.append(result_dict)
    
    # Return json
    return jsonify(result_list)

@app.route("/api/v1.0/<start_date>")
def tobs_start_date(start_date):
    """ Query data for min, max and avg temperatur observables
     from the start date input by user until the last day on the DataBase """

    print("Request received for 'tobs_start_date' page...")

    # Extract data base on start_date to end of the list
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    # Extract data to be jsonify
    result_list = [{"Start Date": start_date}]
    for min, max, avg in result:
        result_dict = {}
        result_dict["TMIN"] = min
        result_dict['TAVG'] = avg
        result_dict['TMAX'] = max
        result_list.append(result_dict) 

    # Return json
    return jsonify(result_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_start_date_end_date(start_date,end_date):
    """ Query data for min, max and avg temperatur observables
     from the start date until the end date input by user """

    print("Request received for 'tobs_start_date_end_date' page...")

    # Extract data base on start_date to end of the list
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
    session.close()

    # Extract data to be jsonify
    result_list = [{"Start Date": start_date, "End Date": end_date}]
    for min, max, avg in result:
        result_dict = {}
        result_dict["TMIN"] = min
        result_dict['TAVG'] = avg
        result_dict['TMAX'] = max
        result_list.append(result_dict) 

    # Return json
    return jsonify(result_list)

def most_recent_date_def():
    """Query the data for the last date 
        inserted in Measurement table"""

    # Start session
    session = Session(engine)

    # Set Variables
    most_recent_date = session.query(Measurement.date)[-1]
    most_recent_date[0]
    

    # Convert most_recent_date to be used for datatime
    year = int(most_recent_date[0][:4])
    month = int(most_recent_date[0][5:7])
    day = int(most_recent_date[0][8:])

    recent_date = dt.date(year, month, day)
    
    # Calculate the date one year from the last date in data set.
    query_date_1year = recent_date - dt.timedelta(days=365)

    return (query_date_1year)


if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    app.run(debug=True)