"""
Nose tests for acp_times.py

Write your tests HERE AND ONLY HERE.
"""

import nose    # Testing framework
import logging


from pymongo import MongoClient
import os
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.mydb

def test_brevets_insert():
    db.races.insert_one({"open": '2021-01-01 00:00:00', "close": '2021-02-01 00:00:00', "km": '100', "miles": '60', "brevet": '100', "time": '2021-01-01 00:00:00'})
    assert(db.races.find({},{ "_id": 0 }) == {"open": '2021-01-01 00:00:00', "close": '2021-02-01 00:00:00', "km": '100', "miles": '60', "brevet": '100', "time": '2021-01-01 00:00:00'})

def test_brevets_retrieval():
    db.races.insert_one({"open": '2021-04-01 10:30:00', "close": '2021-05-01 10:30:00', "km": '350', "miles": '300', "brevet": '300', "time": '2021-03-01 12:30:00'})
    assert(db.races.find({},{ "_id": 0 }) == {"open": '2021-04-01 10:30:00', "close": '2021-05-01 10:30:00', "km": '350', "miles": '300', "brevet": '300', "time": '2021-03-01 12:30:00'})
