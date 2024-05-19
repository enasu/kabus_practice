import json
import os
import re
import glob
from datetime import datetime
from pymongo import MongoClient, ASCENDING, UpdateOne
from mongodb import MongoDBManager
from  utility import time_it 


@time_it
def ticks_for_mongodb(file_path, date_str):
    #  歩み値を銘柄別に保存する　そのため新しい dbを作成
    
    db_name = 'kabu_ticks'
    db = MongoDBManager(db_name)
    date_convert = date_to_microsecond(date_str)
    
    # JSONファイルの読み込み
    #json_file_path = '../data/リスト1_Ticks.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # JSONデータの解析とdatasの作成
    for code, ticks in data['ticks'].items():
        datas=[]
        collection_name = code  #銘柄コード
        for tick in ticks:
            # マッピング情報を用いてデータを再構成
            # pdb.set_trace()
            
            document = {
                'price': tick['p'],
                'timestamp': tick['t'] + date_convert,
                'frame': tick['f'],
                'quantity': tick['q'],
                'kind': tick['k'],
            }
            datas.append(document)
        if datas:    
            db.select_collection(collection_name)
            db.insert_batch(datas)
            # アップサートを考えていたが、同一銘柄同一タイムスタンプのデータが存在する（１回の成り行き発注で
            #複数の価格データが入るため
        
@time_it                        
def fetch_ticks_after_treatment(processed_date=None):
    # Ticks.jsonをmongodbに保存
    files = glob.glob('mnt_data/*Ticks*.json')
    files.sort(key=lambda x: os.stat(x).st_ctime) 
    if processed_date:
        for file in files:
            date_str = re.search(r'(\d{8})', file).group(1)
            # 比較データを作成
            processed_d = datetime.strptime(processed_date,'%Y%m%d')
            file_date = datetime.strptime(date_str,'%Y%m%d')
            if processed_d < file_date:
                print(f'以下のjsonを処理します: {file}')
                ticks_for_mongodb(file, date_str)
    else:  
        file=files[0]
        date_str = re.search(r'(\d{8})', file).group(1)
        print(f'以下のjsonを処理します: {file}')
        ticks_for_mongodb(file, date_str)
        
def fetch_ticks_json():
    files = glob.glob('mnt_data/*Ticks*.json')
    files.sort(key=lambda x: os.stat(x).st_ctime) 
    
class FetchTicksjson:
    def __init__(self):
        self.files = glob.glob('mnt_data/*Ticks*.json')
        self.files.sort(key=lambda x: os.stat(x).st_ctime) 
    
    def fetch_one(self, num):
        file = self.files[num]
        date_str = re.search(r'(\d{8})', file).group(1)
        return file, date_str
    
    def fetch_files(self):
        files_data=[]
        for file in self.files:
            date_str = re.search(r'(\d{8})', file).group(1)
            data = {'file_path':file, 'data_str': date_str}  
            files_data.append(data)
        return files_data

    def iter_files(self, func):
        item_iter = self._yield_files()
        for item_tuple in item_iter :
            func(item_tuple[0], item_tuple[1])
    
    def _yield_files(self):
        files_data=[]
        for file in self.files:
            date_str = re.search(r'(\d{8})', file).group(1)
            yield file, date_str
    

                
def date_to_microsecond(date_str):
    # 日付データを datetime オブジェクトに変換
    date_part = datetime.strptime(date_str, '%Y%m%d')

    # 日付データのマイクロ秒タイムスタンプ
    return int(date_part.timestamp() * 1_000_000)


if __name__ == '__main__':

    # BriSKから取得した歩み値をmongodbへインサートする
    processed_date=20240517
    fetch_ticks_after_treatment(str(processed_date))
