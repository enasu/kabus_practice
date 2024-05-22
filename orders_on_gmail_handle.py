from mongodb import MongoDBManager
import pandas as pd

class OrderOnGmailTakeout:
    def __init__(self):
        pass
    
    def takeout_mongo(self):
        # mongodbから取り出し dfを返す
        db_name = 'stock_kabu'
        db = MongoDBManager(db_name, 'orders_on_gmail')
        self.df=db.convert_pandas()
    
    def arrange_df(self):
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