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

   
