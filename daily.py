from datetime import timedelta, datetime
from kabusapi import KabustationApi
from ticks_handling import TicksInsertHandling
from mongodb import MongoDBManager
from get_gmail import orders_from_gmail_handler
import os
import pathlib
    

if __name__ == '__main__':
    dt_now = datetime.now()
    today = dt_now.strftime('%Y%m%d') 
    today_microsec= today + '000000'
    yesterday = dt_now - timedelta(days=1)
    yesterday =yesterday.strftime('%Y%m%d')  

    print (f'{today} type(today): {type(today)} yesterday:{yesterday}' )
    params={
        'product': 0 ,
        'updtime': today_microsec,
        'state':5
    }
    
    # kabustationからorder情報を mongodbへ保存
    kabustation_api = KabustationApi(stage='honban')
    datas = kabustation_api.fetch_orders(params=params)
    kabusdb = MongoDBManager('stock_kabu',collection_name='orders')
    # アップサートのキーを定義
    upsert_key = ['ID']
    kabusdb.insert_upsert(datas, upsert_key)
    
    # # gmailから order情報をmongodbへ保存
    today2 = dt_now.strftime('%Y/%m/%d')
    start_datetime = today2 + ' 00:00:00'
    end_datetime = today2 + ' 15:10:00'
    print(start_datetime,end_datetime)
    orders_from_gmail_handler(start_datetime, end_datetime)
    
    # Briskから取得した歩み値をmongodbへ保存
    insert_obj = TicksInsertHandling()
    insert_obj.insert_after_processed(yesterday)
    
