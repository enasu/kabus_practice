from datetime import timedelta, datetime
from kabusapi import KabustationApi
from ticks_handle import TicksInsertHandler
from mongodb import MongoDBManager
from get_gmail import FetchOrderFromGmailApiHandler
from utility import time_it, DateTimeParser, handle_exception
    
@time_it
def insert_kabusapi_order(today_microsec):
    try:
        params={
            'product': 0 ,
            'updtime': today_microsec,
            'state':5
        }
        kabustation_api = KabustationApi(stage='honban')
        api_datas = kabustation_api.fetch_orders(params=params)
        kabusdb = MongoDBManager('stock_kabu',collection_name='orders')
        # アップサートのキーを定義
        upsert_key = ['ID']
        kabusdb.insert_upsert(api_datas, upsert_key)
    except Exception:
        handle_exception()
@time_it
def insert_gmail_order(today_str):
    try:
        start_datetime_str = today_str + ' 00:00:00'
        end_datetime_str = today_str + ' 15:10:00'
        print(f'gmail_startdate: {start_datetime_str},end_date: {end_datetime_str}')
        gmail_handler =FetchOrderFromGmailApiHandler()
        gmail_handler.add_datetime_to_query(start_datetime_str, end_datetime_str)
        # insertは upsert処理
        gmail_handler.exec()
    except Exception:
        handle_exception()
        
@time_it
def insert_ticks(yesterday):
        # ! insert_ticksはバッチ処理なので　重複に注意
    try:
        ticks_handler = TicksInsertHandler()
        ticks_handler.insert_after_processed(yesterday)
    except Exception:
        handle_exception()


if __name__ == '__main__':  
    # 現在の日付と時刻
    dt_now = datetime.now()
    today_str = dt_now.strftime('%Y%m%d') 
    today_microsec = int(dt_now.timestamp() * 1_000_000)
    yesterday = dt_now - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    
    # kabustationからorder情報を mongodbへ保存
    insert_kabusapi_order(today_microsec)
    
    # # # gmailから order情報をmongodbへ保存
    insert_gmail_order(today_str)
    
    # Briskから取得した歩み値をmongodbへ保存
    insert_ticks(yesterday)
