"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from pymongo import MongoClient
import os

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.mydb
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

@app.route("/_insert_times", methods=["POST"])
def _insert_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    input_json = request.json
    km = float(input_json["km"])
    miles = float(input_json["miles"])
    brevet = int(input_json["brevet"])
    time = input_json["time"]
    app.logger.debug("km={}".format(km))
    if(km > (brevet * 1.2)):
        return flask.jsonify({"valid": 0})
    open_time = acp_times.open_time(km, brevet, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    db.races.insert_one({"open": open_time, "close": close_time, "km": km, "miles": miles, "brevet": brevet, "time": time})
    return flask.jsonify({"valid": 1})

@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    brevet = request.args.get('brevet', 200, int)
    time = request.args.get('time')
    open_time = acp_times.open_time(km, brevet, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet, arrow.get(time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/_get_times", methods=["POST"])
def _get_times():
    races = list(db.races.find({},{ "_id": 0 }))
    app.logger.debug("races={}".format(races))
    def sortfunc(e):
        return e['km']
    races.sort(key=sortfunc)
    result = races
    return flask.jsonify(result=result)

@app.route("/_cleardb")
def _cleardb():
    db.races.drop()
    return flask.jsonify({})
#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
