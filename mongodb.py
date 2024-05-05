from pymongo import MongoClient
import os
import time
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


class InsertBatch:
    def __init__(self, db, batch_size=100):
        self.db = db
        self.datas = []
        self.batch_size = batch_size
        
    def add_to_batch_iter(self, iter):
        #   イテレーターを受け入れるメソッド
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_batch(self.datas)
                self.datas=[]
        self.db.insert_batch(self.datas)
        
    def add_to_batch_item(self, item):
        #   通常のデータを受け入れるメソッド
        self.datas.append(item)
        if len(self.datas) == self.batch_size:
            self.db.insert_batch(self.datas)
            self.datas=[]
        self.db.insert_batch(self.datas)
    
    def add_to_upsert_iter(self, iter, upsert_key):
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_upsert(self.datas, upsert_key)
                self.datas=[]
        self.db.insert_upsert(self.datas, upsert_key)
    
    def add_to_upsert_item(self, item, upsert_key):
        self.datas.append(item)
        if len(self.datas) == self.batch_size:
            self.db.insert_upsert(self.datas, upsert_key)
            self.datas=[]
        self.db.insert_upsert(self.datas, upsert_key)


class AddTwoBatch:
    #   htmlの生データを内容を抽出したデータと別に残したいと考えたため
    #   命令文で イテレータから情報を取り出すため現状で使わないかも
    def __init__(self, db1,db2, batch_size=100):
        self.db1 = db1
        self.db2 = db2
        self.datas1 = []
        self.datas2 = []
        self.batch_size = batch_size
        
    def add_to_batch(self, iter):
        for body in iter:
            pdb.set_trace()
            self.datas1.append(body[0])
            self.datas2.append(body[1])
            if len(self.datas1) == self.batch_size:
                self.db1.insert_batch(self.datas1)
                self.datas1=[]
                self.db2.insert_batch(self.datas2)
                self.datas2=[]
        self.db1.insert_batch(self.datas1)
        self.db2.insert_batch(self.datas2)
        
    def add_to_upsert(self, iter, upsert_key):
        #   元は同じデータなので同じupsert_keyと考えている
        for body in iter:
            self.datas1.append(body[0])
            self.datas2.append(body[1])
            if len(self.datas1) == self.batch_size:
                self.db1.insert_upsert(self.datas1, upsert_key)
                self.datas1=[]
                self.db2.insert_upsert(self.datas2, upsert_key)
                self.datas2=[]
        self.db1.insert_upsert(self.datas1, upsert_key)
        self.db2.insert_upsert(self.datas2, upsert_key)