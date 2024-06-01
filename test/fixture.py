from ticks_handle import TicksExtractHandler
import matplotlib.pyplot as plt
import pdb

def fixture_date_set():
        code = 9509
        ticks_obj = TicksExtractHandler()
        ticks_obj.exec(str(code))
        df = ticks_obj.df
        # 使用するデータの確認
        date_list = df['Date'].unique()
        date_list.sort()
        date_list
        ln = len(date_list)
        first_date =date_list[0]
        last_date =date_list[ln-1]
        print(f'start: {first_date} end: {last_date}')
        setups = [
                {'time_unit': 'sec', 'interval': 40, 'usedate': [last_date, last_date]},
                {'time_unit': 'min', 'interval': 5, 'usedate': [last_date, last_date]},
                {'time_unit': 'hour', 'interval': 1, 'usedate': [last_date, last_date]},
                {'time_unit': 'day', 'interval': 1, 'usedate': [first_date,last_date]},
                {'time_unit': 'month', 'interval': 1, 'usedate': [first_date,last_date]},
                {'time_unit': 'year', 'interval': 1, 'usedate': [first_date,last_date]},
                                ]        
        return setups


def plot_drow_obj(drow_obj):
        plt.figure(figsize=(20,8))
        drow_obj
        plt.show()