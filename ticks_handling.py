import json
import os
import re
import glob
import pandas as pd
from datetime import timedelta, datetime
from pymongo import MongoClient, ASCENDING, UpdateOne
from mongodb import MongoDBManager
from  utility import time_it, date_to_microsecond
import pdb


class TicksJsonFileInfo:
    # mnt_data/*Ticks*.json file の　file名と file名に付いている日付データを返す
    def __init__(self):
        self.files = glob.glob('mnt_data/*Ticks*.json')
        self.rename_file_with_date()                        # 日付がはいていないファイルに日付を入れる
    
    def select_one(self, num):
        file = self.files[num]
        date_str = re.search(r'(\d{8})', file).group(1)
        return file, date_str
    
    def get_files_info(self):
        files_data=[]
        for file in self.files:
            date_str = re.search(r'(\d{8})', file).group(1)
            data = {'file_path':file, 'date_str': date_str}  
            files_data.append(data)

        files_data.sort( key=lambda x: x['date_str'])     # date_strでソートする implace で返こするため lost.sort()
        return files_data

    def iter_files_info(self, func):
        item_iter = self._yield_files()
        for item_tuple in item_iter :
            func(item_tuple[0], item_tuple[1])
    
    def _yield_files_info(self):
        for file in self.files:
            date_str = re.search(r'(\d{8})', file).group(1)
            yield file, date_str    
            
    def rename_file_with_date(self):
        for file in self.files:
            match = re.search(r'(\d{8})', file)
            if not match:
            #名前に日時が入っていないTicks.jsonについて 作成日の日付を 入れたファイル名に変更
                creatation_time = os.path.getatime(file)
                date_str = datetime.fromtimestamp(creatation_time).strftime('%Y%m%d')
                base_name = os.path.basename(file)
                new_file_name = re.sub(r"(Ticks)(\.json)",r"\1_{}\2".format(date_str), base_name)
                # Ticke_jsonはその日にしか所得できないので、同じ作成日のファイルはいらない.
                # 現状では、わざわざ取得しに行くのでダブリの判定は不要と判断している
                os.rename(file, os.path.join(os.path.dirname(file), new_file_name))
                print(f'basename: {base_name} ⇒ newname : {new_file_name} ')
        self.files = glob.glob('/mnt/data/*Ticks*.json')

        

class TicksInsertToMongo:
    #   json file のpathを取得して　ファイルを開く　ファイルのdateも取得しておく
    #   kabu_ticks は 銘柄コードを collection にする
    #   流し込む
    def __init__(self):
        db_name ='kabu_ticks'
        self.db = MongoDBManager(db_name)
        
    def read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
        
    def data_mapping(self, data, date_convert):
        for code, ticks in data['ticks'].items():
            documents=[]
            collection_name = code  #銘柄コード
            for tick in ticks:
                # マッピング情報を用いてデータを再構成            
                document = {
                    'price': tick['p'],
                    'timestamp': tick['t'] + date_convert,
                    'frame': tick['f'],
                    'quantity': tick['q'],
                    'kind': tick['k'],
                }
                documents.append(document)
            return collection_name, documents
        
    def exec(self, file_path, date_str):
    
        data = self.read_json(file_path)                                    #jsonfile の 読込
        date_convert = date_to_microsecond(date_str)                        #日付データをmicrosecへ変換　外部関数
        collection_name, documents = self.data_mapping(data, date_convert)  # data を mapping
        if documents:    
            self.db.select_collection(collection_name)                      
            self.db.insert_batch(documents)
                

class TicksInsertHandling:
    def __init__(self):
        glob_obj = TicksJsonFileInfo()
        self.files_data = glob_obj.get_files_info()      # files_info_list は {file_path: hoge , date_str: fuga} のリスト
        self.exec_obj = TicksInsertToMongo()    

    @time_it    
    def insert_after_processed(self, processed_date): 
        c = 0
        if processed_date:
            if not isinstance(processed_date, str):
                processed_date =str(processed_date)
            for file_info in self.files_data:
                processed_d = datetime.strptime(processed_date,'%Y%m%d')
                file_date = datetime.strptime(file_info['date_str'],'%Y%m%d')
                if processed_d < file_date:
                    print(f'以下のjsonを処理します: {file_info["file_path"]}')
                    self.exec_obj.exec(file_info['file_path'], file_info['date_str'])
                    c=c+1
            if c == 0:
                print('処理するデータはありません')
    @time_it        
    def insert_one(self):
        file_info = self.files_data[0]
        print(f'以下のjsonを処理します: {file_info["file_path"]}')
        self.exec_obj.exec(file_info['file_path'], file_info['date_str'])
        

class TicksTakeOutHandling:
    def __init__(self):
        db_name ='kabu_ticks'
        self.db = MongoDBManager(db_name)
        self.datas = None
    def read_from_mongo(self, code, query =None):
        collectiton_name = code
        self.db.select_collection(collectiton_name)
        self.df = pd.DataFrame(self.db.find(query))                        #db.find() はreturn を含んでいる
    
    def make_query(self):
        pass
    def formatting(self):
        self.df['timestamp'] = self.df['timestamp'].apply(lambda x: datetime.fromtimestamp(x / 1_000_000))
        # 'timestamp' 列をインデックスに設定
        self.df.set_index('timestamp', inplace=True)
        self.df.drop('_id', axis=1, inplace=True)
        
    def exec(self, code):
        self.read_from_mongo(code)
        self.formatting()

class TicksReadFromJson:

    def __init__(self):
        file_obj = TicksJsonFileInfo()
        files_info = file_obj.get_files_info()
        self.file_info = files_info[len(files_info)-1]
    # TODO 関数にclass 名を付け init を作成した　後の関数は手つかず
    # TODO 一応 printして上の self.file_info は最新のものであることを確認している
    # TODO また file_pathと date_strを持っている        
    def df_from_ticksjson(self, file_path, stock_code): 
        # ファイルを開いて内容を読み込む
        #file_path = 'mnt_data/リスト1_Ticks20240517.json' を想定
        # stock_code は文字列 stock_code = '9509'
        #ファイル名から日付を取得
        date_str = re.search(r'(\d{8})', file_path).group(1)
        # 日付データを datetime オブジェクトに変換
        date_part = datetime.strptime(date_str, '%Y%m%d')
        # 日付データのマイクロ秒タイムスタンプ
        date_microseconds = int(date_part.timestamp() * 1_000_000)

        with open(file_path, 'r') as file:
            data = json.load(file)
        # mapの情報を取得
        map_info = data['map']
        # 銘柄コードに対応するデータを取得
        ticks_data = data['ticks'][stock_code]
        self.df = pd.DataFrame(ticks_data)
        # map情報を使用してカラム名を設定
        self.df.rename(columns=map_info, inplace=True)
        # 日付データと timestamp データを加算
        self.df['timestamp'] = self.df['timestamp'] + date_microseconds
        # 日付文字列を datetime オブジェクトに変換
        self.df['timestamp'] = self.df['timestamp'].apply(lambda x: datetime.fromtimestamp(x / 1_000_000))
        # 'timestamp' 列をインデックスに設定
        self.df.set_index('timestamp', inplace=True)

        # データフレームの内容を確認
        print(self.df.head())




if __name__ == '__main__':

    # BriSKから取得した歩み値をmongodbへインサートする
    #processed_date=20240517
    #obj = TicksInsertHandling()
    #obj.insert_after_processed(processed_date)    

    #read_obj = TicksReadFromJson()
    #print(read_obj.file_info)
    

    obj = TicksTakeOutHandling()
    obj.read_from_mongo('9509')
    print(obj.datas)
