from pymongo import MongoClient
import os
import time
import pandas as pd
import pdb

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PW = os.getenv('MONGO_PW')


class MongoDBManager:
    def __init__(self, db_name ,collection_name):
        self.client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PW}@mongodb:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.start_count = self.collection.count_documents({})

    def insert_batch(self, datas):
        self.collection.insert_many(datas)
            
    def insert_upsert(self, datas, upsert_key):
        # upsert_keyは、辞書型 ex {'ID': item['ID']}
        for data in datas:
            self.collection.update_one(upsert_key, {'$set':data}, upsert=True)
            
    def check_summary(self):
        end_count = self.collection.count_documents({})
        newdata_count = end_count - self.start_count
        print(f'追加したデータ数:{newdata_count}')
        if newdata_count >1 :
            print(f'追加した最初のデータ:{self.collection.find().skip(self.start_count +1)}')
            print(f'追加した最後のデータ:{self.collection.find().skip(end_count)}')
        elif newdata_count==0:
            print(f'追加データはありません')
        else:
            print(f'追加データは以下の1件です:{self.collection.find().skip(end_count)}')
            
    def fetch_unique_field(self):
        all_keys = set()
        
        for document in self.collection.find():
            all_keys.update(document.keys())

        print(all_keys)

    def find_one(self, filter=None):
        document = self.collection.find_one(filter)
        return  document
    
    def find(self,filter=None):
        document = self.collection.find(filter)
        pdb.set_trace()
        return  document

    def convert_pandas(self, filter=None):
        documents = self.collection.find(filter)
        return pd.DataFrame(list(documents))

    def convert_pd_nestdata(self, filter=None, top_level_fields=None):
        # top_level_fields は リストを想定
        
        documents = self.collection.find(filter)
        flat_data =[]
        for doc in documents:
            for detail in doc['Details']:
                flat_record = {k: v for k,v in detail.items()}
                # 必要に応じて他のトップフィールドを追加
                if top_level_fields:
                    for field in  top_level_fields:
                        flat_record[field] = doc.get(field, None) 
                
                flat_data.append(flat_record)
        return pd.DataFrame(flat_data)

class InsertBatch:
    def __init__(self, db, batch_size=100):
        self.db = db
        self.datas = []
        self.batch_size = batch_size
        
    def add_to_batch_iter(self, iter):
        #   イテレーターを受け入れるメソッド
        #       この場合呼び出しは iterをそのまま引数に入れれば良く for 文は事前に必要ない
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_batch(self.datas)
                self.datas=[]
        self.add_batch_flush()
        
    def add_to_batch_item(self, item):
        #   通常のデータを受け入れるメソッド
        self.datas.append(item)
        if len(self.datas) == self.batch_size:
            self.db.insert_batch(self.datas)
            self.datas=[]

    def add_batch_flush(self):
        if self.datas:
            self.db.insert_batch(self.datas)
    
    def add_to_upsert_iter(self, iter, upsert_key):
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_upsert(self.datas, upsert_key)
                self.datas=[]
        self.add_upsert_flush(self.datas, upsert_key)
    
    def add_to_upsert_item(self, item, upsert_key):
        self.datas.append(item)
        if len(self.datas) == self.batch_size:
            self.db.insert_upsert(self.datas, upsert_key)
            self.datas=[]

    def add_upsert_flush(self, upsert_key):
        if self.datas:
            self.db.insert_upsert(self.datas, upsert_key)
