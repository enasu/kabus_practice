from mongodb import MongoDBManager
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import pdb

class ExtractOrderGmail:
    def __init__(self):
        # mongodbから rodersongmaiを取り出す
        db_name = 'stock_kabu'
        db = MongoDBManager(db_name, 'orders_on_gmail')
        self.df = db.convert_pandas()
        self._format_df()

    def _format_df(self):
        new_df= self.df[['日時','銘柄CD','銘柄','取引種類','約定単価','約定数量','支払金額','受取金額']].copy()
        # `支払金額` 列から '円' とカンマを取り除き、整数型に変換
        new_df.fillna({'支払金額':0, '受取金額':0},inplace=True)
        # `支払金額` 列から '円' とカンマを取り除き、NaNを0で置き換え、整数型に変換
        new_df['約定単価'] = new_df['約定単価'].str.replace('円', '').str.replace(',', '').fillna(0).astype(float)
        new_df['約定数量'] = new_df['約定数量'].str.replace('株', '').str.replace(',', '').fillna(0).astype(int)
        new_df['支払金額'] = new_df['支払金額'].str.replace('円', '').str.replace(',', '').fillna(0).astype(int)
        new_df['受取金額'] = new_df['受取金額'].str.replace('円', '').str.replace(',', '').fillna(0).astype(int)
        new_df['損益'] = new_df['受取金額'] + new_df['支払金額']
        new_df['日時'] = pd.to_datetime(new_df['日時'], format='%Y/%m/%d %H:%M:%S')
        new_df['年月日']=new_df['日時'].dt.date
        new_df['時間']=new_df['日時'].dt.time
        new_df.set_index('日時', inplace=True)
        df_sorted = new_df.sort_index()
        
        self.df = df_sorted
    
    def get_other_data_list(self, code, entry_time, exit_time, plot_lib = 'matplot'):
    #   plot_lib は mplfinance :'mpf' か matplot matplot 

        print('---------------get_other_data_list---------------------')
        print(f'self.df.index(0) >>>{self.df.index[0]}  --- entry_time >>> {entry_time}')

        f_df =  self.df[(self.df.index >= entry_time) & (self.df.index <= exit_time) & (self.df['銘柄CD']==str(code)) ]
        
        type_dict_list = [
                {'trade_type':'信用新規買い',
                    'args':{'type': 'scatter', 'color': 'orange', 'marker':'^','zorder':5, 'label':'entry buy'}},
                {'trade_type':'信用返済売り',
                    'args':{'type': 'scatter', 'color': 'orange', 'marker':'v','zorder':5, 'label':'exit sale'}},
                {'trade_type':'信用新規売り',
                    'args':{'type': 'scatter', 'color': 'yellow', 'marker':'^','zorder':5,'label':'entry sale'}},
                {'trade_type':'信用返済買い',
                    'args':{'type': 'scatter', 'color': 'yellow', 'marker':'v','zorder':5,'label':'exit buy'}},
                ]
        other_data_list = []
                # ローソク足の場合は、indextimestampだと x,y size が違うとエラーがでるので現状使えない
                # ローソク足と同じ時間軸にできないか検討する　⇒　同じローソク足の中に複数の値を描画できない
                # plot_lib == 'mpf'は削除
        for type_dict in type_dict_list:
            trade_type = type_dict.get('trade_type')
            tmpdf = f_df[f_df['取引種類'] == trade_type]
            df = self._resample_df(tmpdf)
            plot_args = type_dict['args']
            del plot_args['type']
       
            x = df.index
            y = df['約定単価']
            other_data_list.append([x, y, plot_args])

        return other_data_list
    
    def _resample_df(self, df):
        new_data=[]
        i = 0
        while i < len(df):
            start_time = df.index[i]
            end_time = start_time + pd.Timedelta(seconds=5) #5秒内を集計
                # 2秒以内のデータを選択
            temp_df = df[(df.index >= start_time) & (df.index <= end_time)]
            # 加重平均単価の計算
            total_quantity = temp_df['約定数量'].sum()
            weighted_average_price = (temp_df['約定単価'] * temp_df['約定数量']).sum() / total_quantity if total_quantity != 0 else 0
            total_earn = temp_df['損益'].sum()
            # 新しいデータの保存
            new_data.append({
                'timestamp': start_time,
                '約定数量': total_quantity,
                '約定単価': weighted_average_price,
                '損益' : total_earn
            })
            # 次の開始点を更新
            i += len(temp_df)
        # 新しいDataFrameを作成
        new_df = pd.DataFrame(new_data)
        new_df.set_index('timestamp',inplace=True)
        df_sorted = new_df.sort_index()
        
        return df_sorted



        
        