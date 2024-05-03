from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

## スコープを変更した場合はtoken.jsonを削除してください
SCOPES = ['<https://www.googleapis.com/auth/gmail.readonly>']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # 認証フローが初めて完了したときに自動的にtoken.jsonが作成されます
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 使用可能な認証情報がない場合は、ユーザーにログインを要求します
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=9090)
        # 新しい認証情報をtoken.jsonに保存します。
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Gmail API呼び出し
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - 適切にエラーを処理してください
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
