from pymongo import MongoClient
from pprint import pprint
import certifi

#client = MongoClient("mongodb://localhost:27017/")
#print(client.list_database_names())
#mydb = client["database"]

# Requires the PyMongo package.
# https://api.mongodb.com/python/current
uri = "mongodb+srv://m001-student:m001-mongodb-basics@sandbox.sjafx.mongodb.net/M001?retryWrites=true&w=majority"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client.sample_airbnb
result = db["listingsAndReviews"].aggregate([
    {
        '$group': {
            '_id': '$room_type',
            'count': {
                '$sum': 1
            }
        }
    }
])
for x in result:
    print(x)
result = db['listingsAndReviews'].aggregate([
    {
        '$group': {
            '_id': '$room_type',
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$limit': 2
    }
])
for x in result:
    print(x)

