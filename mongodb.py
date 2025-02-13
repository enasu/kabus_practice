from pymongo import MongoClient, UpdateOne
import os
import pandas as pd
from utility import time_it, handle_exception
import pdb

class MongoDBManager:
    def __init__(self, db_name ,collection_name=None):
        self.MONGO_USER = os.getenv('MONGO_USER')
        self.MONGO_PW = os.getenv('MONGO_PW')        
        self.client = MongoClient(f'mongodb://{self.MONGO_USER}:{self.MONGO_PW}@mongodb:27017/')
        self.db = self.client[db_name]
        self.collection = None
        # collectionを一度に指定するために下で定義したメッソッドを呼び出す
        if collection_name:
            self.select_collection(collection_name) 
            self.start_count = self.collection.count_documents({})
    
    def select_collection(self, collection_name):
        # collectionが動的に変更する場合に対応
        self.collection = self.db[collection_name]
        
    def list_collection_names(self):
        # このメソッドを追加して、内部のdbオブジェクトからコレクション名を取得
        return self.db.list_collection_names()
    
    @time_it
    def insert_batch(self, datas):
        try:
            result = self.collection.insert_many(datas)
            print(type(result))
            print(f'collection : {self.collection}')
            print(f'batch処理しました 最初のデータ{datas[0]}')
        except Exception:
            handle_exception()
    
    #@time_it
    def insert_upsert(self, datas, upsert_key):
        # upsert_keyは、リストで取得 ex ['ID', 'user']         
        bulk_operations = []            # バルク操作のためのリストを初期化
        try:
            for data in datas:
                upsert_key_dict = {k: data[k] for k in upsert_key if k in data}
                operation = UpdateOne(upsert_key_dict, {'$set':data}, upsert=True)
                bulk_operations.append(operation)
        #except Exception as e:
        #    print(f'mongodbmanager の insert_upsert で エラーが発生しました count : {c} その時のdata : {data}')    
        # バルク操作の実行
            if bulk_operations:
                result = self.collection.bulk_write(bulk_operations)    
                print(f'type(result) --matched :{result.matched_count} -- modified :{result.modified_count}')
        except Exception:
            handle_exception()    
            
    def insert_upsert_one(self, data, upsert_key):
        try:
            upsert_key_dict = {k: data[k] for k in upsert_key if k in data}
            result = self.collection.update_one(upsert_key_dict, {'$set':data}, upsert=True)
            print(f'{type(result)} ')
        except Exception:
            handle_exception()
            
    def check_unique_field(self):
        all_keys = set()
        
        for document in self.collection.find():
            #   documentによってkeyが異なる可能性があるため回している
            all_keys.update(document.keys())

        return all_keys

    def find_one(self, filter=None):
        document = self.collection.find_one(filter)
        return  document
    
    @time_it
    def find(self,filter=None):
        document = self.collection.find(filter)
        return  document

    @time_it
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
            


        
    
