import concurrent.futures
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from get_gmail import GmailApi
from mongodb import MongoDBManager
from utility import time_it, DateTimeParser
import pdb

# 作成途中 時間短縮のため
def fetch_and_save_email_data(executor, service, db_manager, user_id, query):
    try:
        
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get('messages', [])
        pdb.set_trace()
        if messages:
            executor.submit(save_data_to_db, db_manager, messages)

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            # 新しいページのデータ取得も非同期で実行
            executor.submit(fetch_page_data, executor, service, db_manager, user_id, query, page_token)
    except HttpError as error:
        print(f'An error occurred: {error}')


def fetch_page_data(executor, service, db_manager, user_id, query, page_token):
    try:
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages = response.get('messages', [])
        if messages:
            pdb.set_trace()
            executor.submit(save_data_to_db, db_manager, messages)

        # 次のページがあればさらに非同期で取得
        if 'nextPageToken' in response:
            next_page_token = response['nextPageToken']
            executor.submit(fetch_page_data, executor, service, db_manager, user_id, query, next_page_token)
    except HttpError as error:
        print(f'An error occurred: {error}')


# データベースへのデータ保存を非同期的に行う関数の定義
def save_data_to_db(db_manager, data):
    if data:
        db_manager.insert_upsert(data, upsert_key=['gmail_id'])

# 非同期処理のメインロジック
@time_it
def main(start_datetime, end_datetime):
    gmail_api = GmailApi()
    service = gmail_api.service  # Gmail APIの認証
    parser_after = DateTimeParser(start_datetime)
    after = parser_after.unix_time
    parser_befor = DateTimeParser(end_datetime)
    before = parser_befor.unix_time
    query = f'from:support@kabu.com subject:"【auKabucom】約定通知 " after:{after} before:{before}'
    db_manager = MongoDBManager('your_db_name', 'your_collection_name')

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 初回のメールデータ取得と保存を非同期で開始
        pdb.set_trace()
        executor.submit(fetch_and_save_email_data, executor, service, db_manager, query)

if __name__ == '__main__':
    start_datetime = '20240521 00:00:00'
    end_datetime = '20240521 15:30:00'
    main(start_datetime,end_datetime)
