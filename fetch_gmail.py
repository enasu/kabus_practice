import os
import sys
import pickle
import base64
from datetime import datetime
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from mongodb import MongoDBManager
from  utility import time_it, DateTimeParser ,handle_exception
import pdb

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class GmailApi:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] # スコープの設定
        self.creds = self.authenticate()
        self.service=build('gmail', 'v1', credentials=self.creds)
    
    def authenticate(self):
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
                        '/data/credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=9990)    # docker container から実行する為 defaultは port=0
                # 新しいトークンを保存
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        except Exception:
            handle_exception()
            # 既存のトークンファイルが問題の原因かもしれないため削除
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
            # 新しい認証プロセスを強制的に実行
            flow = InstalledAppFlow.from_client_secrets_file(
                '../data/credentials.json', self.SCOPES)
            creds = flow.run_local_server(port=9990)
            # 新しいトークンを保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def get_message_iter(self, query):
        '''
        gmail api は デフォルトで100件、最大500件の取得しかできないので
        nextPageToken を利用する
        '''  
        # 現状自分の id だけしかとれない 
        results = self.service.users().messages().list(userId='me', q=query).execute()
        
        while True:
            messages = results.get('messages',[])
            for message in messages:
                full_message = self.service.users().messages().get(userId='me', id=message['id'], 
                                                                    format='full').execute()
                yield full_message
                
            # nextPageTokenが存在するか確認し、あれば次のページのデータを取得
            page_token = results.get('nextPageToken')
            if page_token:
                results = self.service.users().messages().list(userId='me', q=query, 
                                                            pageToken=page_token).execute()
            else:
                break
   

class Parse_email_content_orders:
    def __init__(self):
        pass
    
    def body_content(self, full_message):
        parts = full_message['payload'].get('parts', [])
        message_id = full_message.get('id')
        body_content = {}

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
            return self.parse_email_content(body_content['html'], message_id) , \
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
            # ! 修正した 日時
            datetime_str = details[0].strip()
            data['日時'] = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
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


class FetchOrderFromGmailApiHandler:
    def __init__(self):
        db_name = 'stock_kabu'
        self.db_orders = MongoDBManager(db_name, 'orders_on_gmail_new')
        self.db_html = MongoDBManager(db_name, 'orders_html')
        self.query ='from:support@kabu.com subject:"【auKabucom】約定通知 "'
        self.parse_obj = Parse_email_content_orders()
        self.body_contents = []
        self.htmls =[]
    @time_it
    def exec(self):
        upsert_key=['gmail_id']
        gmail_api=GmailApi()
        try:
            message_iter = gmail_api.get_message_iter(self.query)
            for message in message_iter:
                item_tuple = self.parse_obj.body_content(message)
                self.body_contents.append(item_tuple[0])
                self.htmls.append(item_tuple[1])
            self.db_orders.insert_upsert(self.body_contents, upsert_key)
            self.db_html.insert_upsert(self.htmls, upsert_key)
            self.body_contents = []
            self.htmls =[]
        except Exception:
            handle_exception()
            raise
        
            
    def add_datetime_to_query(self, start_datetime_str, end_datetime_str):
        # datetime はstr '2024/05/22 00:00:00'
        try:
            #gmail api は unixtimeで指定 
            parser_after = DateTimeParser(start_datetime_str)
            after = parser_after.unix_time
            parser_befor = DateTimeParser(end_datetime_str)
            before = parser_befor.unix_time
            self.query = self.query + f' after:{after} before:{before}'
        except Exception:
            handle_exception()
            raise


if __name__ == '__main__':
    start_datetime = '20240201 00:00:00'
    end_datetime = '20240612 15:30:00'
    gmail_handler = FetchOrderFromGmailApiHandler()
    gmail_handler.add_datetime_to_query(start_datetime,end_datetime)
    gmail_handler.exec()