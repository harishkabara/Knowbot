import json
import ast
import sys
import jsonify
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['chatbot']
collection = db['NLPdb']
result=collection.find()
for res in result:
    print(res)
#collection.update_one(
    #{"question": "how is life"},
    #{"$set":
       # {"answer": "life is good1",
        #"token": ["how","life","good"]
   # }})