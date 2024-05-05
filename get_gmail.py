import os
import sys
import pickle
import base64
import re
from datetime import datetime, timezone, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mongodb import MongoDBManager, InsertBatch
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# スコープの設定
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    # すでに保存されたトークンがあれば読み込み
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    try:
        # トークンがない場合、ユーザー認証を行う
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '../data/credentials.json', SCOPES)
                creds = flow.run_local_server(port=9990)    # docker container から実行する為 defaultは port=0
            # 新しいトークンを保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    except Exception as e:
        print(f"トークンのリフレッシュに失敗しました: {e}")
        # 既存のトークンファイルが問題の原因かもしれないため削除
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        # 新しい認証プロセスを強制的に実行
        flow = InstalledAppFlow.from_client_secrets_file(
            '../data/credentials.json', SCOPES)
        creds = flow.run_local_server(port=9990)
        # 新しいトークンを保存
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def datetime_to_unixtime(date_str):
    # 日時文字列をdatetimeオブジェクトに変換（JSTとして解釈）
    dt = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
    # JSTをUTCに変換
    dt_utc = dt - timedelta(hours=9)  # JSTはUTC+9
    # UNIX時間（エポック秒）に変換
    unixtime = int(dt_utc.replace(tzinfo=timezone.utc).timestamp())
    return unixtime

class BatchEmailBody:
    def __init__(self, creds, query, batch_size=100):
        self.service = build('gmail', 'v1', credentials=creds)
        self.results = self.service.users().messages().list(userId='me', q=query).execute()
        self.messages = self.results.get('messages', [])
        self.batch_size =batch_size
        self.datas = []
        print(f'class生成時のemailの件数:{len(self.messages)}')

    def generate_body(self):
        if not self.messages:
            print('No messages found.')
            return []
        # 各メッセージの本文を取得
        for message in self.messages:
            yield self.get_email_body(message['id'])

    def add_to_batch(self, iter):
        for body in iter:
            self.datas.append(body)
            if len(self.datas) == self.batch_size:
                self.db.insert_batch(self.datas)
                self.datas=[]
        self.db.insert_batch(self.datas)

    def get_email_body(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        parts = message['payload'].get('parts', [])
        body_content = {}
        #pdb.set_trace()        
        for part in parts:
            mime_type = part['mimeType']
            data = part['body'].get('data', '')
            if data:
                decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                if mime_type == 'text/plain':
                    body_content['text'] = decoded_data
                elif mime_type == 'text/html':
                    body_content['html'] = decoded_data

        if 'html' in body_content:
            return self.parse_email_content(body_content['html'], message_id), \
                {'gmail_id': message_id, 'html': body_content['html']}    # データ切出し(上の行）と生のhtmlを返す
                # key 'gmail_id` は upsert_keyに利用するため def parse_email_contentと合わせた
                
    def parse_email_content(self, html_content, message_id):
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
    
def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} の実行時間: {end_time - start_time:.6f} 秒")
        return result
    return wrapper

@time_it
def exec():
    creds = authenticate()
    db_name = 'stock_kabu'
    db_orders = MongoDBManager(db_name, 'orders_on_gmail')
    db_html = MongoDBManager(db_name, 'orders_html')
    # 期間指定
    start_datetime = '2024/01/24 00:00:00'
    end_datetime = '2024/05/03 15:30:00'
    after = datetime_to_unixtime(start_datetime)
    before = datetime_to_unixtime(end_datetime)
    query = f'from:support@kabu.com subject:"【auKabucom】約定通知 " after:{after} before:{before}'
    batch_method_orders = InsertBatch(db_orders)
    batch_method_html = InsertBatch(db_html)
    get_iter = BatchEmailBody(creds, query)
    body_iter = get_iter.generate_body()
    #   イテレータから　情報を取り出す処理
    #       複数データをイテレータでとりだすため一旦取り出してデータとして渡す必要がある
    for item_list in body_iter:
        batch_method_orders.add_to_batch_item(item_list[0])
        batch_method_html.add_to_batch_item(item_list[1])
    #   batch_size に満たないデータが入っているときの処理
    #       イテレータとして渡していないのでここで事後処理が必要
    batch_method_orders.add_batch_flush()
    batch_method_html.add_batch_flush()
    
@time_it
def exec2():
    # get_iter.genereate_body() で複数のデータを処理しないように変更
    creds = authenticate()
    db_name = 'stock_kabu'
    db_orders = MongoDBManager(db_name, 'orders_on_gmail')
    db_html = MongoDBManager(db_name, 'orders_html')
    # 期間指定
    start_datetime = '2024/01/24 00:00:00'
    end_datetime = '2024/05/03 15:30:00'
    after = datetime_to_unixtime(start_datetime)
    before = datetime_to_unixtime(end_datetime)
    query = f'from:support@kabu.com subject:"【auKabucom】約定通知 " after:{after} before:{before}'
    batch_method_orders = InsertBatch(db_orders)
    batch_method_html = InsertBatch(db_html)
    get_iter = BatchEmailBody(creds, query)
    body_iter = get_iter.generate_body()
    #   イテレータから　情報を取り出す処理
    #       複数データをイテレータでとりだすため一旦取り出してデータとして渡す必要がある
    for item_list in body_iter:
        batch_method_orders.add_to_batch_item(item_list[0])
        batch_method_html.add_to_batch_item(item_list[1])
    #   batch_size に満たないデータが入っているときの処理
    #       イテレータとして渡していないのでここで事後処理が必要
    batch_method_orders.add_batch_flush()
    batch_method_html.add_batch_flush()


if __name__ == '__main__':
    exec()