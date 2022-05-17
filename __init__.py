from flask import Flask, render_template, request, make_response, jsonify
from geopy.geocoders import Nominatim
import pymongo


class mongo_connection:
    conn = None

    def connect(self):
        myclient = pymongo.MongoClient(
            "mongodb+srv://Drmohm:Ferum%402664@mar.sibmp.mongodb.net/?retryWrites=true&w=majority")
        mydb = myclient["Project_MAR"]
        self.conn = mydb["restaurants"]

    def query(self, sql):
        cursor = self.conn.find(sql)
        return cursor


db = mongo_connection()
db.connect()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/rest', methods=['GET'])
def getrestaurats():
    restname = request.args.get('restaurant')
    city = request.args.get('city')
    state = request.args.get('state')
    zipcode = request.args.get('zipcode')
    rad = request.args.get('radius')
    print(rad)
    print(type(rad))

    print(restname, city, state, zipcode)

    zip_or_addr = city + ' ' + state + ' ' + zipcode

    print(f'zip_or_addr: {zip_or_addr}')

    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(zip_or_addr)
    lat = float(location.raw['lat'])
    lon = float(location.raw['lon'])
    nearby_restaurants = [{'orig_lat': lat, 'orig_lon': lon}]

    print(lat, lon)

    METERS_PER_MILE = 1609.34

    filters = {'location': {'$nearSphere': {'$geometry': {'type': "Point",
                                                          'coordinates': [float(lon), float(lat)]},
                                            '$maxDistance': int(rad) * METERS_PER_MILE}},
               'name': {'$regex': restname, "$options": "i"}}

    cursor = db.query(filters)


    for cur in cursor:
        print(cur)
        nearby_restaurants.append({
            'restaurant_name': cur['name'],
            'lat': cur['location']['coordinates'][1],
            'lon': cur['location']['coordinates'][0]
        })
    #nearby_restaurants=[{'orig_lat': 40.3754434, 'orig_lon': 49.8326748}, {'restaurant_name': 'Derya Fish House', 'lat': 40.304027636182674, 'lon': 49.827603950210836}]
    print(nearby_restaurants)
    return jsonify(nearby_restaurants)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000, debug=True)