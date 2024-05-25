from datetime import datetime, timezone
import time
import traceback
import sys
import pdb

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} の実行時間: {end_time - start_time:.6f} 秒")
        return result
    return wrapper

def handle_exception():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)
    last_call = tb[-1]
    print(f"エラーが発生した関数: {last_call.name}")
    print(f"エラーメッセージ: {exc_value}")

class DateTimeParser:
    def __init__(self, date_str):
        self.date_formats ={'date_only_with_slash': '%Y/%m/%d', 
                'date_only_without_slash': '%Y%m%d',
                'with_slash': '%Y/%m/%d %H:%M:%S',
                'without_slash': '%Y%m%d %H:%M:%S'
                }
        self.format = None
        self.date_part = None
        self.unix_time = None
        self.microsec = None
        self.convert_dt_obj(date_str)

    def convert_dt_obj(self, date_str):
        if '/' in date_str:
            if len(date_str) <= 10 :
                self.format = self.date_formats.get('date_only_with_slash')
            else:
                self.format = self.date_formats.get('with_slash')        
        else:
            if len(date_str) <= 8 :
                self.format = self.date_formats.get('date_only_without_slash')
            else:
                self.format = self.date_formats.get('without_slash')
        self.date_part = datetime.strptime(date_str, self.format)
        self.microsec =int(self.date_part.timestamp() * 1_000_000)
        self.unix_time =int(self.date_part.replace(tzinfo=timezone.utc).timestamp())
        
