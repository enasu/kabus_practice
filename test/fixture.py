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

# test用
def plot_df_test(data_dict):
        plt.figure(figsize=(20,8))        
        df = data_dict.get('df')
        if df is None or df.empty:
                raise ValueError('DataFrame is empty or not provided')
        x = df.index
        y = df['約定単価']
        args = data_dict['args']
        
        plot_type =data_dict.get('plot_type')
        if plot_type:
                # matplot 
                if plot_type =='scatter':
                        args.pop('type', None)  # 'type'を削除
                        plt.scatter(x,y, **args)
                
                #elif args['type']=='line':
                else:
                        args.pop('type', None)  # 'type'を削除
                        plt.plot(x, y, **args)
                
        else:
                # TODO 一応 mpf を想定しているが下のコードは対応していない 　mpfの場合 date_dictの構造が違う
                plt.plot(df, **args)
                
        
        plt.show()   