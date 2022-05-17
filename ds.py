from urllib.parse import quote_plus
from pymongo import MongoClient
from geopy.geocoders import Nominatim
passw=quote_plus('Ferum@2664')

client = MongoClient("mongodb+srv://Drmohm:"+passw+"@mar.sibmp.mongodb.net/?retryWrites=true&w=majority")

db = client.Project_MAR

rest=db.restaurants
#rest.create_index({'location':'2dsphere'})

c=rest.find({'location': {'$near': {'$geometry': {'type': "Point",
                                                          'coordinates': [126.77, 37.649]},
                                            '$maxDistance': 1}},
               'name': {'$regex': "ken", "$options": "i"}}
          )




d=rest.find({'location': {'$nearSphere': {'$geometry': {'type': 'Point', 'coordinates': [-73.9, 40.7]}, '$maxDistance': 804600.7}}, 'name': {'$regex': 'der', '$options': 'i'}, "rank":{"$ge":3}})
bak_find=rest.find({"name":"Derya Fish House"})
for i in bak_find:
    print(i)
name=str(input('restaurant: '))
index=input('index number: ')
rank=input('rank: ')
loc=Nominatim(user_agent="app")
city = loc.geocode("8 Aziz Aliyev St")
print(city.raw)
rest.insert_one({"location":{"coordinates":[float(city.raw['lon']),float(city.raw['lat'])], "type":"Point"},"name":name, "rank": rank})
print(city)