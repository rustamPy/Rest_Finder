from flask import Flask, render_template, request, make_response, jsonify
from geopy.geocoders import Nominatim
import pymongo


class mongo_connection:
    col = None

    def connect(self):
        myclient = pymongo.MongoClient("localhost", 27017)
        mydb = myclient["restdb"]
        self.col = mydb["restaurants"]

    def query(self, sql):
        cursor = self.col.find(sql)
        return cursor

    def setrest(self, val):
        self.col.insert_one(val)


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

@app.route('/api/rest', methods=['GET'])
def getrestaurants():
    restname = request.args.get('restaurant')
    addr=request.args.get('addr')
    city=request.args.get('city')
    rad = request.args.get('radius')
    rank= request.args.get('rank')
    print(rad)
    print(type(rad))

    print(restname)

    final_addr=addr+' '+city

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
                                            '$maxDistance': METERS_PER_MILE*int(rad)}},
               'name': {'$regex': restname, "$options": "i"},
               'rank':{'$gt':int(rank)}}
    #
    print(filters)
    cursor = db.query(filters)
    print(cursor)
    for cur in cursor:
        print(cur)
        nearby_restaurants.append({
            'restaurant_name': cur['name'],
            'lat': cur['location']['coordinates'][1],
            'lon': cur['location']['coordinates'][0],
            'rank':rank
        })
    # nearby_restaurants=[{'orig_lat': 40.3754434, 'orig_lon': 49.8326748}, {'restaurant_name': 'Derya Fish House', 'lat': 40.304027636182674, 'lon': 49.827603950210836}]
    print(f'nearby rests --> {nearby_restaurants}')
    return jsonify(nearby_restaurants)


@app.route('/api/rest', methods=['SET'])
def setrestaurants():
    restname = request.args.get('restaurant')
    addr=request.args.get('addr')
    rank= request.args.get('rank')
    print(restname)
    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(addr)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    succ="Congrats!"
    data = {"location": {"coordinates": [float(lon), float(lat)], "type": "Point"}, "name": restname, "rank": int(rank)}
    db.setrest(data)

    return succ


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000, debug=True)
