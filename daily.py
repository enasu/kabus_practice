from datetime import timedelta, datetime, time
from kabusapi import KabustationApi
from ticks_handle import TicksExtractHandler, TicksInsertHandler
from mongodb import MongoDBManager
from fetch_gmail import FetchOrderFromGmailApiHandler
from plot_timestamp_data import PlotTimeStamp
from extract_orders_on_gmail import ExtractOrderGmail
from utility import time_it, DateTimeParser, PeriodFilterMaker , handle_exception
import pandas as pd
import pdb
    

def insert_kabusapi_order(date_time_str):
    try:
        params={
            'product': "0" ,
            'updtime':int(date_time_str),
            'state':"5" 
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
        end_datetime_str = today_str + ' 15:35:00'
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
        # TODO  get error yesterday format
        ticks_handler.insert_after_processed(yesterday)
    except Exception:
        handle_exception()
        
def plot_timestamp(start_time, end_time,interval_minutes=60):
    
    fil={'日時': {'$gte':start_time ,'$lte': end_time}}
    print(f'条件:{fil}')
    gmail_obj = ExtractOrderGmail(fil)
    df = gmail_obj.df
    codes = df['銘柄CD'].unique()
    ticks_obj = TicksExtractHandler()
    
    for code in codes:
        print(f'表示する銘柄CD>>>{code}')
        ticks_obj.exec(str(code))
        other_draw_data_list = gmail_obj.get_orderdata_by_symbol(code, start_time, end_time, plot_lib="matplot")
        plot_obj = PlotTimeStamp( ticks_obj.df, other_draw_data_list)
        plot_obj.plot(str(code), start_time, end_time)
        interval = pd.Timedelta(minutes=interval_minutes)
        plot_obj.continuous_display_within_period(start_time, end_time, interval)
        
class PlotTimestamp:
    def __init__(self, start_time, end_time):
        fil = {'日時': {'$gte':start_time ,'$lte': end_time}}
        self.start_time = start_time
        self.end_time = end_time
        print(f'条件:{fil}')
        self.gmail_obj = ExtractOrderGmail(fil)
        self.df = self.gmail_obj.df
        self.codes = self.df['銘柄CD'].unique()
        self.ticks_obj = TicksExtractHandler()
        
    def plot_map(self, interval_minutes=60):
        interval = pd.Timedelta(minutes=interval_minutes)
        for code in self.codes:
            print(f'表示する銘柄CD>>>{code}')
            self.ticks_obj.exec(str(code))
            other_draw_data_list = self.gmail_obj.get_orderdata_by_symbol(
                                        code, self.start_time, self.end_time, plot_lib="matplot")
            plot_obj = PlotTimeStamp( self.ticks_obj.df, other_draw_data_list)
            plot_obj.plot(str(code), self.start_time, self.end_time)
            plot_obj.continuous_display_within_period(self.start_time, self.end_time, interval)
        
        
class DailyHandler:
    def __init__(self):
        dt_now = datetime.now()
        # 当日の午前0時を取得
        self.today = datetime.combine(dt_now.date(), time.min)
        self.today_str = today.strftime('%Y%m%d')
        
    def all_day(self):
        dt_now = datetime.now()
        # 当日の午前0時を取得
        today = datetime.combine(dt_now.date(), time.min)
        today_str = today.strftime('%Y%m%d')
        date_time_str = today.strftime('%Y%m%d%H%M%S')  # 日付と時刻をYYMMDDHHMMSS形式で
        today_microsec = int(today.timestamp() * 1_000_000) # Ticks_data は当日の時間データだけなので、日付をひっつけて日時データとする
        # 当日の午前9時と午後3時を設定
        start_time = datetime.combine(dt_now.date(), time(9, 0))
        end_time = datetime.combine(dt_now.date(), time(15, 30))
        # pandasのdatetime形式で出力
        start_time_pd = pd.to_datetime(start_time)
        end_time_pd = pd.to_datetime(end_time)


        # 昨日の午前0時を取得
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y%m%d')
        yesterday_datetime_str = yesterday.strftime('%Y%m%d%H%M%S')
            


if __name__ == '__main__':  

    # 現在の日時を取得
    dt_now = datetime.now()
    # 当日の午前0時を取得
    today = datetime.combine(dt_now.date(), time.min)
    today_str = today.strftime('%Y%m%d')
    date_time_str = today.strftime('%Y%m%d%H%M%S')  # 日付と時刻をYYMMDDHHMMSS形式で
    today_microsec = int(today.timestamp() * 1_000_000)
    # 当日の午前9時と午後3時を設定
    start_time = datetime.combine(dt_now.date(), time(9, 0))
    end_time = datetime.combine(dt_now.date(), time(15, 30))
    # pandasのdatetime形式で出力
    start_time_pd = pd.to_datetime(start_time)
    end_time_pd = pd.to_datetime(end_time)


    # 昨日の午前0時を取得
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    yesterday_datetime_str = yesterday.strftime('%Y%m%d%H%M%S')
    
    
    # kabustationからorder情報を mongodbへ保存
    #
    insert_kabusapi_order(date_time_str)
    
    
    # gmailから order情報をmongodbへ保存
    insert_gmail_order(today_str)
    
    # Briskから取得した歩み値をmongodbへ保存
        # 前日の値から今日の値を取得している
    #
    insert_ticks(yesterday_str)
  
    #plot_timestamp(start_time_pd, end_time_pd)
