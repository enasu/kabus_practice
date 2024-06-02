from plot_step_val import PlotStepValue
from test.fixture import fixture_date_set
from utility import DateTimeParser, handle_exception
from extract_orders_on_gmail import ExtractOrderGmail
from ticks_handle import TicksExtractHandler
from plot_timestamp_data import GetPlotObjTimeStamp
from extract_orders_on_gmail import ExtractOrderGmail
from datetime import datetime as dt
import datetime                         # from datetime import datetime とは別のモジュール　timeメッソッドを持っている
import pandas as pd
import pdb


def test_plot_step_value():
        setups = fixture_date_set()
        c = 0
        code = 9509     
        ticks_obj = TicksExtractHandler()
        ticks_obj.exec(code)
        gmail_obj = ExtractOrderGmail()
        df = ticks_obj.df
        try:
                for set_up in setups:
                        c=+1
                        print(f'set_up: {c} 回目')
                        time_unit = set_up.get('time_unit')
                        interval = set_up.get('interval')
                        enter_date = set_up.get('usedate')[0]
                        enter_time = dt.combine(enter_date, datetime.time(8,59,0))
                        exit_date = set_up.get('usedate')[1]
                        exit_time = dt.combine(exit_date, datetime.time(15,1,0))
                        
                        filtered_df = df[(df.index >= enter_time) & (df.index <= exit_time)]
                        print(f'set_up-{c} enter_date {enter_date}  == type{type(enter_date)}')
                        print(f'entar_time {enter_time}  == type: {type(enter_time)}')
                        print(f'df.index[0] {df.index[0]}  == type: {type(df.index[0])}')
                        print(f' 期間 {enter_time}>>{exit_time}  time_unit : {time_unit}  interval : {interval} のPlotStepValue のテスト---------------')
                        
                        # other data を追加
                        
                        orher_data_draw_obj_list = gmail_obj.get_other_data_list(code, enter_time, exit_time,plot_lib='mpf')
                        pdb.set_trace()
                        plot_obj = PlotStepValue(filtered_df, interval, time_unit, orher_data_draw_obj_list)


                        plot_obj.plot_candlestick()
        except Exception:
                handle_exception()
                



if __name__ == '__main__':
        test_plot_step_value()

