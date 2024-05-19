import json
import pandas as pd
from datetime import timedelta, datetime
import mplfinance as mpf
import re

class PlotStepValue:
    # 使用するdata ⇒ df
    # index:    timestamp micro秒 datetimeオブジェクト
    # price:    float
    # quantity : int
    # その他はあっても良い
    def __init__(self, moto_df, interval, time_unit = 'min'):
        self.interval_str = self.set_interval( interval, time_unit )
        self.df_resamped = self.resample_df(moto_df)
    
    def set_interval(self, interval, time_unit = 'sec'):
        # time_unit のマッピングを辞書で定義
        time_units = {
            'sec': 's',
            'min': 'min',
            'hour': 'H',
            'day': 'D',
            'mon': 'M',
            'year': 'Y'
        }
            # time_unit の値に基づいて適切な単位を取得
        unit = time_units.get(time_unit, 'min')  # デフォルト値として 's' を使用⇒修正
        # interval 引数を文字列に変換し、単位を追加
        return str(interval) + unit
        
    def resample_df(self, df):
        ohlc_dict ={
        'price': 'ohlc',
        'quantity':'sum'
       }
        # 1分ごとにリサンプリングして OHLC データを計算
        df_resampled = df.resample(self.interval_str).apply(ohlc_dict)
        # columns を修正
        df_resampled.columns = [ 'Open', 'High', 'Low', 'Close', 'Volume']
        #11時31分から12:29までのデータを削除
        df_resampled = df_resampled[(df_resampled.index.time < pd.to_datetime('11:31').time()) \
                                    | (df_resampled.index.time > pd.to_datetime('12:29').time())]
        # 移動平均線を計算
        df_resampled['SMA_20'] = df_resampled['Close'].rolling(window=20).mean()
        df_resampled['SMA_50'] = df_resampled[ 'Close'].rolling(window=50).mean()
        return df_resampled
            
    def plot_candlestick(self):
        # カスタムスタイルの設定
        mc = mpf.make_marketcolors(up='r', down='g', edge='i', wick='i', volume='in', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='gray')

        # ローソクチャートを描画
        mpf.plot(self.df_resamped, type='candle', style= s, \
                    figsize=(20,8), title= self.interval_str +' Candlestick Chart', \
                    ylabel='Price', ylabel_lower='Volume')

                
class GetDFFromTicksjson:
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
        self.df['timestamp'] = self.df['timestamp'] + date_microseconds
        # 日付文字列を datetime オブジェクトに変換
        self.df['timestamp'] = self.df['timestamp'].apply(lambda x: datetime.fromtimestamp(x / 1_000_000))
        # 'timestamp' 列をインデックスに設定
        self.df.set_index('timestamp', inplace=True)

        # データフレームの内容を確認
        print(self.df.head())
