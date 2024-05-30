from plot_step_val import PlotStepValue
from test.fixture import fixture_date_set, plot_df_test
from utility import DateTimeParser, handle_exception
from test.extract_order_test import test_extract_order_on_gmail
from ticks_handle import TicksExtractHandler
from datetime import datetime as dt
import datetime                         # from datetime import datetime とは別のモジュール　timeメッソッドを持っている
import pdb


def test_plot_step_value():
        setups = fixture_date_set()
        c = 0
        code = 9509     
        ticks_obj = TicksExtractHandler()
        ticks_obj.exec(code)
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
                        print(f' 期間 {enter_time}>>{exit_time}  time_unit : {time_unit}  interval : {interval} のPlotStepValue のテスト---------------')
                        
                        # other data を追加
                        add_data_list = test_extract_order_on_gmail(code, enter_date, exit_date)
                        
                        plot_obj = PlotStepValue(filtered_df, interval, time_unit, add_data_list)
                        print(f'plot_obj.interval_set :{plot_obj.interval_set} === title : {plot_obj.title_unit}')                

                        print(f'plot_obj.df_resampled のtype >>> {plot_obj.df_resampled.dtypes}')

 
                        order_df= add_data_list[1]['df']
                        #pdb.set_trace()
                        
                        order_dict = {'df': order_df}
                        plot_df_test(order_dict)  


                        #plot_obj.plot_candlestick()
        except Exception:
                handle_exception()
                




if __name__ == '__main__':
        test_plot_step_value()