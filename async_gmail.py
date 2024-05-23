import concurrent.futures
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from get_gmail import authenticate, datetime_to_unixtime
from mongodb import MongoDBManager

# 作成途中

def fetch_and_save_email_data(executor, service, db_manager, user_id, query):
    try:
        
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get('messages', [])
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
def main(start_datetime, end_datetime):
    cred = authenticate()
    service = build('gmail', 'v1', credentials=cred)  # Gmail APIの認証
    after = datetime_to_unixtime(start_datetime)
    before = datetime_to_unixtime(end_datetime)
    query = f'from:support@kabu.com subject:"【auKabucom】約定通知 " after:{after} before:{before}'
    db_manager = MongoDBManager('your_db_name', 'your_collection_name')

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 初回のメールデータ取得と保存を非同期で開始
        executor.submit(fetch_and_save_email_data, executor, service, db_manager, query)

if __name__ == '__main__':
    main()
