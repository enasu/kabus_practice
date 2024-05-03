from pymongo import MongoClient
import urllib.request
import json
import os

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PW = os.getenv('MONGO_PW')

def insert_data_to_mongodb(content, table):
    # MongoDBへの接続設定
    # user名:pw
    # 'authSource'は認証情報を持つデータベース、通常は'admin'ですが、設定によって異なる場合があります。
    client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PW}@mongodb:27017/')
    db = client['stock_kabu']
    colleciton = db['table']

    try:
            # MongoDBにデータを挿入
        for item in content:

            # アップサートのキーを定義
            upsert_key = {'ID': item['ID']}
            colleciton.update_one(upsert_key,{'$set':item}, upsert=True)

        print("最初の5件のデータ:")
        for item in colleciton.find().limit(5):
            print(item)

        # 総件数を取得
        total_count = colleciton.count_documents({})
        print(f'総件数:{total_count}')

        # 最後の5件のデータを表示
        print("最後の5件のデータ:")
        if total_count > 5:
            for item in colleciton.find().skip(total_count - 5):
                print(item)

    except Exception as e:
        print(f"An error occurred: {e}")


class MongoDBManager:
    def __init__(self, db_name='stock_kabu', collection_name='your_collection', batch_size=100):
        self.client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PW}@mongodb:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.batch = []
        self.batch_size = batch_size

    def add_to_batch(self, data):
        #   yieldでdataを追加する事を前提としている
        self.batch.append(data)
        if len(self.batch) == self.batch_size:
            
            self.insert_batch()

    def insert_batch(self):
        if self.batch:
            self.collection.insert_many(self.batch)
            self.batch = []

    def finalize(self):
        self.insert_batch()
