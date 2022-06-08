"""
Rustam Karimov
ID: 17915
"""

from flask import Flask, render_template, request, make_response, jsonify
from geopy.geocoders import Nominatim
import pymongo
import os

class mongo_connection:
    col = None
    def connect(self):
        myclient = pymongo.MongoClient("localhost", 27017)
        mydb = myclient["restdb"]
        self.col = mydb["new_restaurants"]

    def query(self, sql):
        cursor = self.col.find(sql)
        return cursor

    def setrest(self, val):
        self.col.insert_one(val)

    def remrest(self, val):
        self.col.delete_one(val)


db = mongo_connection()
db.connect()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("main.html")


@app.route('/add')
def add_site():
    return render_template("add.html")


@app.route('/search')
def search_site():
    return render_template("search.html")


@app.route('/delete')
def delete_site():
    return render_template("delete.html")


@app.route('/api/rest', methods=['GET'])
def getrestaurants():
    restname = request.args.get('restaurant')
    addr = request.args.get('addr')
    city = request.args.get('city')
    rad = request.args.get('radius')
    rank = request.args.get('rank')
    print(rad)
    print(type(rad))
    if not rank:
        rank = 0
    if not rad:
        rad = 1000
    if not addr:
        addr = "Wroclaw 53-100"

    print(restname)

    final_addr = addr + ' ' + city

    print(f'Address is: {final_addr}')

    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(final_addr)

    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    nearby_restaurants = [{'orig_lat': lat, 'orig_lon': lon}]
    print(nearby_restaurants)
    print(lon, lat)

    METERS_PER_MILE = 1609.34

    filters = {'location': {'$nearSphere': {'$geometry': {'type': "Point",
                                                          'coordinates': [float(lon), float(lat)]},
                                            '$maxDistance': METERS_PER_MILE * int(rad)}},
               'name': {'$regex': restname, "$options": "i"},
               'rank': {'$gte': float(rank)}}

    print(filters)
    cursor = db.query(filters)
    print(cursor)
    for cur in cursor:
        print(cur)
        nearby_restaurants.append({
            'restaurant_name': cur['name'],
            'lat': cur['location']['coordinates'][1],
            'lon': cur['location']['coordinates'][0],
            'rank': cur['rank']
        })
    print(f'nearby rests --> {nearby_restaurants}')
    return jsonify(nearby_restaurants)


@app.route('/api/rest', methods=['SET'])
def setrestaurants():
    restname = request.args.get('restaurant')
    addr = request.args.get('addr')
    rank = request.args.get('rank')
    print(restname)
    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(addr)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    data = {"location": {"coordinates": [float(lon), float(lat)], "type": "Point"}, "name": restname, "rank": float(rank)}
    db.setrest(data)
    return True

@app.route('/api/rest', methods=['REM'])
def remrestaurants():
    restname = request.args.get('restaurant')
    print(restname)
    data_rem = {'name': {'$regex': restname, "$options": "i"}}
    db.remrest(data_rem)
    return jsonify(data_rem)

if __name__ == "__main__":
    app.run(host='127.0.0.2', port=1313, debug=True)
