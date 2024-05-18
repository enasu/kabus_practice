import time

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} の実行時間: {end_time - start_time:.6f} 秒")
        return result
    return wrapper