import concurrent.futures
from googleapiclient.errors import HttpError
from get_gmail import authenticate

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
def main():
    service = authenticate()  # Gmail APIの認証
    user_id = 'your_user_id_here'
    query = 'from:someone@example.com subject:"Important"'
    db_manager = MongoDBManager('your_db_name', 'your_collection_name')

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 初回のメールデータ取得と保存を非同期で開始
        executor.submit(fetch_and_save_email_data, executor, service, db_manager, user_id, query)

if __name__ == '__main__':
    main()
