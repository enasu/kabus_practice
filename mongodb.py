from pymongo import MongoClient, UpdateOne
import os
import time
import pandas as pd
from utility import time_it
import pdb

class MongoDBManager:
    def __init__(self, db_name ,collection_name=None):
        self.MONGO_USER = os.getenv('MONGO_USER')
        self.MONGO_PW = os.getenv('MONGO_PW')        
        self.client = MongoClient(f'mongodb://{self.MONGO_USER}:{self.MONGO_PW}@mongodb:27017/')
        self.db = self.client[db_name]
        self.collection = None
        if collection_name:
            self.select_collection(collection_name) 
            self.start_count = self.collection.count_documents({})
    
    def select_collection(self, collection_name):
        # collectionが動的に変更する場合に対応
        self.collection = self.db[collection_name]
        
    def list_collection_names(self):
        # このメソッドを追加して、内部のdbオブジェクトからコレクション名を取得
        return self.db.list_collection_names()

    def insert_batch(self, datas):
        result = self.collection.insert_many(datas)
        print(type(result))
        print(f'collection : {self.collection}')
        print(f'batch処理しました 最初のデータ{datas[0]}')
            
    def insert_upsert(self, data, upsert_key):
        # upsert_keyは、リストで取得 ex ['ID', 'user'] 
        # バルク操作のためのリストを初期化
        c=0
        bulk_operations = []
        c=c+1
        try:
            upsert_key_dict = {k: data[k] for k in upsert_key if k in data}
            operation = UpdateOne(upsert_key_dict, {'$set':data}, upsert=True)
            bulk_operations.append(operation)
        except Exception as e:
            print(f'mongodbmanager の insert_upsert で エラーが発生しました count : {c} その時のdata : {data}')
            
        # バルク操作の実行
        if bulk_operations:

            self.collection.bulk_write(bulk_operations)    
            
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
            
    def check_unique_field(self):
        all_keys = set()
        
        for document in self.collection.find():
            #   documentによってkeyが異なる可能性があるため回している
            all_keys.update(document.keys())

        return all_keys

    def find_one(self, filter=None):
        document = self.collection.find_one(filter)
        return  document
    
    def find(self,filter=None):
        document = self.collection.find(filter)
        return  document

    def convert_pandas(self, filter=None):
        # TODO 別に移すか　削除する
        documents = self.collection.find(filter)
        return pd.DataFrame(list(documents))

    def convert_pd_nestdata(self, filter=None, top_level_fields=None):
        # TODO 別に移すか　削除する
        # top_level_fields は リストを想定
        
        documents = self.collection.find(filter)
        flat_data =[]
        for doc in documents:
            for detail in doc['Details']:                       # このdhiteilsは特定のデータの形式　汎用化するか 削除するか
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
        
    def use_batch_from_iter(self, iter):
        #   イテレーターを受け入れるメソッド
        #       この場合呼び出しは iterをそのまま引数に入れれば良く for 文は事前に必要ない
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_batch(self.datas)
                self.datas=[]
        self.use_insert_batch_flush()
    
    @time_it   
    def use_insert_batch(self, item):
        #   通常のデータを受け入れるメソッド
        self.datas.append(item)
        if len(self.datas) == self.batch_size:
            self.db.insert_batch(self.datas)
            self.datas=[]

    def use_insert_batch_flush(self):
        if self.datas:
            self.db.insert_batch(self.datas)
    
