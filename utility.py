from datetime import datetime, timezone, timedelta
import time
import traceback
import sys

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
    # トレースバック全体をフォーマットして表示
    formatted_traceback = traceback.format_tb(exc_traceback)
    print("トレースバックの詳細:")
    for trace in formatted_traceback:
        print(trace)
    
def print_dict_structure(d, indent=0):
    for key, value in d.items():
        print('  ' * indent + f"{key}: {type(value)}")
        if isinstance(value, dict):
            print_dict_structure(value, indent + 1)
        elif isinstance(value, list):
            print('  ' * (indent + 1) + f"List of {len(value)} items")
            # リストの最初の要素のみを調査することでリスト内の構造を推測
            if value and isinstance(value[0], dict):
                print_dict_structure(value[0], indent + 2)

class DateTimeParser:
    def __init__(self, date_str):
        self.date_formats ={'date_only_with_slash': '%Y/%m/%d', 
                'date_only_without_slash': '%Y%m%d',
                'with_slash': '%Y/%m/%d %H:%M:%S',
                'without_slash': '%Y%m%d %H:%M:%S'
                }
        self.format = None
        self.date_std = None
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
        self.date_std = datetime.strptime(date_str, self.format)
        self.microsec =int(self.date_std.timestamp() * 1_000_000)
        self.unix_time =int(self.date_std.replace(tzinfo=timezone.utc).timestamp())

    def get_previous_day(self):
        previous_day = self.date_std - timedelta(days=1)
        previous_day_str = previous_day.strftime(self.format)
        return DateTimeParser(previous_day_str)
