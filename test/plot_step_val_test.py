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
                

def get_plot_object_timestamp_simple():
    df = pd.DataFrame({
    '約定単価': [100, 200, 300, 400, 500],
    '日付': pd.date_range(start='2024-06-01', periods=5, freq='D')
    })
    df.set_index('日付', inplace=True)

    # クラスのインスタンスを作成してプロットを行う
    plotter = GetPlotObjTimeStamp(df)
    plotter.get_period(pd.Timestamp('2024-06-02'), pd.Timestamp('2024-06-04')) 
    

def get_plot_object_timestamp():
        code=9509
        ticks_obj = TicksExtractHandler()
        ticks_obj.exec(str(code))
        ticks_df = ticks_obj.df
        
        start_time = pd.to_datetime('2024-05-30 09:00:00.000000')
        end_time = pd.to_datetime('2024-05-30 12:00:00.000000')
        gmail_obj = ExtractOrderGmail()
        other_draw_data_list = gmail_obj.get_other_data_list(code, start_time, end_time, plot_lib="matplot")
        
        plot_obj = GetPlotObjTimeStamp(ticks_df, other_draw_data_list)
        plot_obj.get_plot(start_time, end_time)


if __name__ == '__main__':
        #test_plot_step_value()

        #get_plot_object_timestamp_simple()
        get_plot_object_timestamp()