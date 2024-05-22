from datetime import datetime
import time

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} の実行時間: {end_time - start_time:.6f} 秒")
        return result
    return wrapper

            
def date_to_microsecond(date_str):
    # 日付データを datetime オブジェクトに変換
    date_part = datetime.strptime(date_str, '%Y%m%d')

    # 日付データのマイクロ秒タイムスタンプ
    return int(date_part.timestamp() * 1_000_000)