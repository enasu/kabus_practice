import json
import pandas as pd
from datetime import timedelta, datetime
from workalendar.asia import Japan  # workalendar を利用して日本の祝日を管理
import matplotlib.pyplot as plt
import mplfinance as mpf
from utility import handle_exception
import re
import pdb

class GetPlotObjStepVal:
    def __init__(self,main_df, other_data_list=None):
        self.main_df = main_df
        self.other_data_list = other_data_list
        self.other_subset_list=[]
        
    def get_plot(self,title_str,start_time, end_time):
        pass
        

class PlotStepValue:
    # 使用するdata ⇒ df
    # index:    timestamp micro秒 datetimeオブジェクト
    # price:    float
    # quantity : int
    # その他はあっても良い
    
    def __init__(self, moto_df, interval, time_unit, other_data_draw_obj_list =None ):
        self.cal = Japan()
        self.interval_set, self.title_unit = self._set_interval( interval, time_unit )
        self.df_resampled = self._resample_df(moto_df)
        self.interval_str = str(interval)
        self.plot_args = None
        self.addplot = []
        self.other_data_draw_obj_list =other_data_draw_obj_list

    def _set_interval(self, interval, time_unit ):
        # time_unit のマッピングを辞書で定義
        time_units_dict = {
            'sec': {'unit':'s','title':'Seconds'},
            'min': {'unit':'min','title':'Minutes'},
            'hour': {'unit':'H','title':'Hour'},
            'day': {'unit':'D','title':'Day'},
            'month': {'unit':'M','title':'Month'},
            'year':{'unit':'Y','title':'Year'},
        }
        tmp_dict = time_units_dict.get(time_unit)
        print(f'tmp_dict : {tmp_dict}')
        unit = tmp_dict.get('unit')
        title = tmp_dict.get('title')
        
        return str(interval) + unit, title 
        
    def _resample_df(self, df):
        ohlc_dict ={
        'price': 'ohlc',
        'quantity':'sum'
       }
        # 1分ごとにリサンプリングして OHLC データを計算
        df_resampled = df.resample(self.interval_set).apply(ohlc_dict)
        # columns を修正
        df_resampled.columns = [ 'Open', 'High', 'Low', 'Close', 'Volume']
        #11時31分から12:29までのデータを削除
        if self.title_unit in ['Seconds','Minutes','hour']:
            df_resampled = self._remove_lunchtime(df_resampled)
        
        df_resampled = self._remove_suspens_day(df_resampled)

        # 移動平均線を計算
        df_resampled['SMA_5'] = df_resampled['Close'].rolling(window=5).mean()
        df_resampled['SMA_24'] = df_resampled['Close'].rolling(window=24).mean()
        df_resampled['SMA_60'] = df_resampled[ 'Close'].rolling(window=60).mean()
        df_resampled['SMA_100'] = df_resampled[ 'Close'].rolling(window=100).mean()
        return df_resampled
    
    def _remove_lunchtime(self,df_resampled):
        #11時31分から12:29までのデータを削除
        df_convert = df_resampled[(df_resampled.index.time < pd.to_datetime('11:31').time()) \
                                    | (df_resampled.index.time > pd.to_datetime('12:29').time())]        
        return df_convert
        
    def _remove_suspens_day(self, df_resampled):
        #祝休日を削除
        df_convert = df_resampled[
            ~(
                (df_resampled.index.weekday == 5) |  # 土曜日
                (df_resampled.index.weekday == 6) |  # 日曜日
                (df_resampled.index.map(self.is_holiday))  # 祝日
            )
        ]
        # 15:00以降 9:00以前のデータを削除
        df_convert = df_convert[
            (
                (df_convert.index.time >= pd.to_datetime('9:00').time()) &
                (df_convert.index.time <= pd.to_datetime('15:00').time())
                )]
        
        return df_convert
    
    def is_holiday(self, date):
        try:
            # 指定された日付が祝日かどうかを判定
            return self.cal.is_holiday(date.date())    
        except Exception:
            handle_exception()
            raise
          
    def _get_addplot_sma(self):
        # 利用可能なカラーマップから色を取得
        cmap = plt.get_cmap("viridis")
        
        # "SMA_"で始まるカラムを見つける
        sma_columns = [col for col in self.df_resampled.columns if col.startswith('SMA_')]
        
        # 色の数を決定
        colors = [cmap(i / len(sma_columns)) for i in range(len(sma_columns))]
        
        # 各SMAカラムに対してaddplotを作成
        for i, col in enumerate(sma_columns):
            if self.df_resampled[col].notna().any():
                self.addplot.append(
                    mpf.make_addplot(self.df_resampled[col], color=colors[i], linestyle='--')
                )
            
    def _add_other_data(self):
        # ! 使えない　timestampでの描画の参考に残すが後で削除
        print('--------------- def _add_order_data ----------------')
        if self.other_data_draw_obj_list:
        #    for other_data_obj in self.other_data_draw_obj_list:
        # self.addplot.append(other_data_obj)
            other_data_obj = self.other_data_draw_obj_list[1]
            self.addplot.append(other_data_obj)
            
    def _set_argument(self):
        # カスタムスタイルの設定 ローソク足
        mc = mpf.make_marketcolors(up='g', down='r', edge='i', wick='i', volume='in', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='gray')
        self.plot_args = {
            'type': 'candle',
            'style': s, 
            'figsize': (20, 8),
            'volume': True,
            'title': self.interval_str + self.title_unit + ' Candlestick Chart',
            'ylabel': 'Price',
            'ylabel_lower': 'Volume',
        }

        if self.addplot:
            self.plot_args['addplot'] = self.addplot
                
    def plot_candlestick(self):
        # 移動平均線の追加
        self._get_addplot_sma()
        if self.other_data_draw_obj_list:
            self._add_other_data()
        self._set_argument()
        # ローソクチャートを描画

        mpf.plot(self.df_resampled, **self.plot_args)


class CalcSMA:
    patterns = [['SMA_3','SMA_12'],
           ['SMA_3','SMA_15'],
           ['SMA_3','SMA_20'],
           ['SMA_3','SMA_24'],
           ['SMA_5','SMA_12'],
           ['SMA_5','SMA_15'],
           ['SMA_5','SMA_20'],
           ['SMA_5','SMA_24'],
           ['SMA_6','SMA_12'],
           ['SMA_6','SMA_15'],
           ['SMA_6','SMA_24'],
           ['SMA_5','SMA_24','SMA_60','SMA_100'],
          ]
    def __init__(self, moto_df, pattern):
        self.df = moto_df 
   
