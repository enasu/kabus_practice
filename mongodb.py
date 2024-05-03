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

def generate_data():
    # この関数はジェネレータとしてデータを生成します
    for i in range(1000):  # 1000個のデータを生成する例
        yield {'name': f'User{i}', 'age': i % 50}


class BatchEmailBody:
    def __init__(self, creds, query, db, batch_size=100):
        self.service = build('gmail', 'v1', credentials=creds)
        self.results = self.service.users().messages().list(userId='me', q=query).execute()
        self.messages = self.results.get('messages', [])
        self.db = db
        self.batch_size =batch_size
        self.datas = []
    
    def add_to_batch(self, message):
        body = self.get_email_body(self.service, message['id'])
        self.datas.append(body)
        if len(self.datas) == self.batch_size:
            self.db.insert_batch()
        self.db.insert.finalize()

    def generate_body(self):
        if not self.messages:
            print('No messages found.')
            return []
        # 各メッセージの本文を取得
        for message in self.messages:
            yield self.add_to_batch(message)
            
    def get_email_body(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        parts = message['payload'].get('parts', [])
        body_content = {}
        for part in parts:
            mime_type = part['mimeType']
            data = part['body'].get('data', '')
            if data:
                decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                if mime_type == 'text/html':
                    body_content['html'] = decoded_data

        #print(f"Message ID: {message_id}")
        if 'html' in body_content:
            print("HTML Part: ", body_content['html'])
            self.parse_email_content(body_content['html'], message_id)

    def parse_email_content(html_content, message_id):
        data = {}
        data['gmail_id'] = message_id

        # 約定しましたの後の行二段下げから次の行二段下げまでの間を抽出
        pattern = r'約定しました。<br/><br/>(.*?)<br/><br/>'
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            details = match.group(1).split('<br/>')

            # 日時
            data['日時'] = details[0].strip()

            # CXJ9509／北海道電力
            market_info = details[1].strip()
            market_parts = market_info.split('／')
            code_parts = re.match(r"([\w\W]+?)(\d+)", market_parts[0].strip())
            if code_parts:
                data['市場'] = code_parts.group(1)
                data['銘柄CD'] = code_parts.group(2)
            data['銘柄'] = market_parts[1].strip()

            # 信用返済買い／指値
            transaction_info = details[2].strip()
            transaction_parts = transaction_info.split('／')
            data['取引種類'] = transaction_parts[0].strip()
            data['指値/成行'] = transaction_parts[1].strip()

            # その後の改行から二段下げまでの間
            additional_info = details[3:]
            for info in additional_info:
                if info.strip():
                    key_value = info.strip().split(' ')
                    if len(key_value) == 2:
                        data[key_value[0]] = key_value[1]

        return data          