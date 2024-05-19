from pymongo import MongoClient
from mongodb import MongoDBManager 


def check_data_type_on_mongo_ticks():
    db_name = 'kabu_ticks'
    db = MongoDBManager(db_name)
    collections = db.list_collection_names()
    collection = collections[0]
    db.select_collection(collection)
    doc = db.find_one()
    fields = db.fetch_unique_field()
    
    for field in fields:
        print(f' field名 : {field} - value : {doc[field]} - filed type : {type(field)}')
        


    
    
    
    