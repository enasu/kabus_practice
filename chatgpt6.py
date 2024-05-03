import os
import sys
import pickle
import json
import base64
import re
from datetime import datetime, timezone, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .mongodb import MongoDBManager

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# スコープの設定
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    # すでに保存されたトークンがあれば読み込み
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # トークンがない場合、ユーザー認証を行う
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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

def get_emails(creds, start_datetime, end_datetime):
    service = build('gmail', 'v1', credentials=creds)
    # UNIX時間に変換
    after = datetime_to_unixtime(start_datetime)
    before = datetime_to_unixtime(end_datetime)
    # メールを検索
    query = f'from:support@kabu.com subject:"【auKabucom】約定通知 " after:{after} before:{before}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
 
    if not messages:
        print('No messages found.')
        return []

    # 各メッセージの本文を取得
    for message in messages:
        yield get_email_body(service, message['id'])
    
def get_email_body(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
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
        parse_email_content(body_content['html'], message_id)

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

class GenerateDate:
    def __init__(self, db, batch_size=100):
        self.data = []
        self.db = db    # MongoDBManager インスタンス
        self.batch_size = batch_size
        
    def gene(self, body_content):
        self.data.append(body_content)
        if len(self.data) == self.batch_size:
            self.db.add_to_batch(self.data)
            self.data=[]

if __name__ == '__main__':
    creds = authenticate()
    db_name = 'stock_kabu'
    db_collection = 'orders_on_gmail'
    db_manager = MongoDBManager(db_name, db_collection)
    # 期間指定
    start_datetime = '2024/04/26 14:41:00'
    end_datetime = '2024/04/26 14:42:00'
    for data in get_emails(creds, start_datetime, end_datetime):
        db_manager.add_to_bacth(data)
    db_manager.finalize()
