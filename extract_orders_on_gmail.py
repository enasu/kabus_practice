from mongodb import MongoDBManager
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
        new_df['支払金額'] = new_df['支払金額'].str.replace('円', '').str.replace(',', '').fillna(0).astype(int)
        new_df['受取金額'] = new_df['受取金額'].str.replace('円', '').str.replace(',', '').fillna(0).astype(int)
        new_df['損益'] = new_df['受取金額'] + new_df['支払金額']
        new_df['日時'] = pd.to_datetime(new_df['日時'], format='%Y/%m/%d %H:%M:%S')
        new_df['年月日']=new_df['日時'].dt.date
        new_df['時間']=new_df['日時'].dt.time
        new_df.set_index('日時', inplace=True)
        
        self.df = new_df
    
    
def get_contract_df(code, entry_time, exit_time):
        gmail_obj = ExtractOrderGmail()
        gmail_df = gmail_obj.df
        f_df =  gmail_df[(gmail_df.index >= entry_time) & (gmail_df.index <= exit_time) & (gmail_df['銘柄CD']==str(code)) ]
        
        type_dict_list = [
                {'trade_type':'信用新規買い',
                 'args':{'type': 'scatter', 'color': 'blue', 'marker':'^', 's':100,'zorder':5, 'label':'entry buy'}},
                {'trade_type':'信用返済売り',
                 'args':{'type': 'scatter', 'color': 'blue', 'marker':'v', 's':100,'zorder':5, 'label':'exit sale'}},
                {'trade_type':'信用新規売り',
                 'args':{'type': 'scatter', 'color': 'yellow', 'marker':'^', 's':100,'zorder':5,'label':'entry sale'}},
                {'trade_type':'信用返済買い',
                 'args':{'type': 'scatter', 'color': 'yellow', 'marker':'v', 's':100,'zorder':5,'label':'exit buy'}},
                ]
        for type_dict in type_dict_list:
            trade_type = type_dict.get('trade_type')
            df = f_df[f_df['取引種類'] == trade_type]
            type_dict['df'] = df
            type_dict['column_name'] = '約定単価'
            
        return type_dict_list
            
            