import json
import pandas as pd
from datetime import timedelta, datetime
from workalendar.asia import Japan  # workalendar を利用して日本の祝日を管理
import mplfinance as mpf
from utility import handle_exception
import re
import pdb

class PlotStepValue:
    # 使用するdata ⇒ df
    # index:    timestamp micro秒 datetimeオブジェクト
    # price:    float
    # quantity : int
    # その他はあっても良い
    
    def __init__(self, moto_df, interval, time_unit,other_data_draw_obj_list =None ):
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
            df_resampled = self._remnove_lunchtime(df_resampled)
        if self.title_unit == 'Day':
            df_resampled = self._remove_suspens_day(df_resampled)

        # 移動平均線を計算
        df_resampled['SMA_20'] = df_resampled['Close'].rolling(window=20).mean()
        df_resampled['SMA_50'] = df_resampled[ 'Close'].rolling(window=50).mean()
        return df_resampled
    
    def _remnove_lunchtime(self,df_resampled):
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
        return df_convert
    
    def is_holiday(self, date):
        try:
            # 指定された日付が祝日かどうかを判定
            return self.cal.is_holiday(date.date())    
        except Exception:
            handle_exception()
            raise
          
    def _get_addplot_sma(self):
        if self.df_resampled['SMA_20'].notna().any():
            self.addplot.append(mpf.make_addplot(self.df_resampled['SMA_20'], color='blue', linestyle='--'))

        # SMA_50が存在し、有効なデータがあるか確認
        if self.df_resampled['SMA_50'].notna().any():
            self.addplot.append(mpf.make_addplot(self.df_resampled['SMA_50'], color='orange', linestyle='--'))
            
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
        #self._get_addplot_sma()
        if self.other_data_draw_obj_list:
            self._add_other_data()
        self._set_argument()
        # ローソクチャートを描画

        mpf.plot(self.df_resampled, **self.plot_args)

   
