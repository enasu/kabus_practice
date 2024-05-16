from pymongo import MongoClient
from datetime import datetime
import os
import pprint

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PW = os.getenv('MONGO_PW')

# MongoDB クライアントの設定
client = MongoClient(f'mongodb://{MONGO_USER}:{MONGO_PW}@mongodb:27017/')
db = client['stock_kabu']  # データベース名を指定
collection = db['orders']  # コレクション名を指定

# 検索する日付の範囲を設定
start = datetime(2024, 5, 13, 14, 0, 0)
end = datetime(2024, 5, 13, 14, 59, 59)


# 日付の範囲に一致するドキュメントを検索
results = collection.find({
    'Details.ExecutionDay': {
        '$gte': start.isoformat(),
        '$lte': end.isoformat()
    }
})

# 結果の出力
for result in results:
    pprint.pprint(result)

