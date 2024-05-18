import json
import pandas as pd
from datetime import timedelta, datetime
import mplfinance as mpf
import re

class PlotStepValue:
    def __init__(self):
        pass
    
    # 日付データと timestamp データを結合
    def combine_date_and_time(self, microseconds, date_part):
        # timedeltaを使用してマイクロ秒を時間に変換
        time_part = (datetime.min + timedelta(microseconds=microseconds)).time()
        # 日付と時間を結合して文字列に変換
        datetime_str = f"{date_part} {time_part}"
        return datetime_str 
    
    def df_from_ticksjson(self, file_path, stock_code): 
        # ファイルを開いて内容を読み込む
        #file_path = 'mnt_data/リスト1_Ticks20240517.json' を想定
        # stock_code は文字列 stock_code = '9509'
        #ファイル名から日付を取得
        date_str = re.search(r'(\d{8})', file_path).group(1)
        # 日付データを datetime オブジェクトに変換
        date_part = datetime.strptime(date_str, '%Y%m%d')
        # 日付データのマイクロ秒タイムスタンプ
        date_microseconds = int(date_part.timestamp() * 1_000_000)

        with open(file_path, 'r') as file:
            data = json.load(file)
        # mapの情報を取得
        map_info = data['map']
        # 銘柄コードに対応するデータを取得
        ticks_data = data['ticks'][stock_code]
        self.df = pd.DataFrame(ticks_data)
        # map情報を使用してカラム名を設定
        self.df.rename(columns=map_info, inplace=True)
        # 日付データと timestamp データを加算
        self.df['timestamp'] = df['timestamp'] + date_microseconds
        # 日付文字列を datetime オブジェクトに変換
        self.df['timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x / 1_000_000))
        # 'timestamp' 列をインデックスに設定
        self.df.set_index('timestamp', inplace=True)

        # データフレームの内容を確認
        print(self.df.head())

        
    def plot_candlestick(self):
        # 'price' 列を float 型に変換
        self.df['price'] = self.df['price'].astype(float)
        # 1分ごとにリサンプリングして OHLC データを計算
        df_resampled = self.df['price'].resample('1T').ohlc()

        # ローソクチャートを描画
        mpf.plot(df_resampled, type='candle', style='charles', title='1-Minute Candlestick Chart', ylabel='Price')