from plot_step_val import PlotStepValue
from ticks_handle import TicksTakeOutHandler
from utility import DateTimeParser, handle_exception
from datetime import datetime as dt
import datetime                         # from datetime import datetime とは別のモジュール　timeメッソッドを持っている
import pandas as pd
import pdb


def test_plot_step_value():
    code = 9509
    ticks_obj = TicksTakeOutHandler()
    ticks_obj.exec(str(code))
    df = ticks_obj.df
    print('--------------PlotStepValue のテスト---------------')
    # 使用するデータの確認
    date_list = df['Date'].unique()
    date_list.sort()
    date_list
    ln = len(date_list)
    first_date =date_list[0]
    last_date =date_list[ln-1]
    print(f'start: {first_date} end: {last_date}')
    setups = [
            {'time_unit': 's', 'interval': 40, 'usedate': [last_date, last_date]},
            {'time_unit': 'min', 'interval': 5, 'usedate': [last_date, last_date]},
            {'time_unit': 'H', 'interval': 1, 'usedate': [last_date, last_date]},
            {'time_unit': 'D', 'interval': 1, 'usedate': [first_date,last_date]},
            {'time_unit': 'M', 'interval': 1, 'usedate': [first_date,last_date]},
            {'time_unit': 'Y', 'interval': 1, 'usedate': [first_date,last_date]},
                        ]
    try:
        for set_up in setups:
                time_unit = set_up.get('time_unit')
                interval = set_up.get('interval')
                enter_date = set_up.get('usedate')[0]
                enter_time = dt.combine(enter_date, datetime.time(8,59,0))
                exit_date = set_up.get('usedate')[1]
                exit_time = dt.combine(exit_date, datetime.time(15,1,0))
                filtered_df = df[(df.index >= enter_time) & (df.index <= exit_time)]
                print(f'enter_date {enter_date}  == type{type(enter_date)}')
                print(f'entar_time {enter_time}  == type: {type(enter_time)}')
                print(f' 期間 {enter_time}>>{exit_time}  time_unit : {time_unit}  interval : {interval} のPlotStepValue のテスト---------------')
                plot_obj = PlotStepValue(filtered_df, interval)
                plot_obj.set_interval(interval, time_unit=time_unit)
                plot_obj.resample_df(filtered_df)
                plot_obj.plot_candlestick()
    except Exception:
            handle_exception()


if __name__ == '__main__':
        test_plot_step_value()