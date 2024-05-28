from ticks_handle import TicksJsonFileInfo, TicksInsertToMongo, TicksReadFromJsonFile, TicksExtractHandler, \
                        TicksInsertHandler
from utility import DateTimeParser, print_dict_structure, handle_exception

def test_ticks_json_file_info(file_obj):
    
    print(f'self.files : {file_obj.files}')
    
    print('--------------def select_one のテスト---------------')
    le = len(file_obj.files)
    file, date_str = file_obj.select_one(0)
    print(f'filesの最初の filepath:{file} 日付は {date_str}')
    file, date_str = file_obj.select_one(le-1)
    print(f'filesの最後の filepath:{file} 日付は {date_str}')
    
    print('--------------def get_files_info のテスト---------------')
    files_data = file_obj.get_files_info()
    print(f'files_dateの最初の辞書は {files_data[0]}')
    le = len(files_data)
    print(f'files_dateの最後の辞書は {files_data[le-1]}')
    

def test_ticks_insert_to_monogo(file_obj):
    insert_obj = TicksInsertToMongo()
    file_tuple = file_obj.select_one(0)
    file_path = file_tuple[0]
    data = insert_obj.read_json(file_path)
    date = file_tuple[1]
    date_parser = DateTimeParser(date)
    date_convert = date_parser.microsec                   #日付データをmicrosecへ変換　外部関数
    print('--------------TickInserToMongo def _data_mapping_iter のテスト---------------')
    c = 0
    iter = insert_obj.data_mapping_iter(data, date_convert)
    for colleciton_name, documents in iter:
        if c == 1 :
            print (f'collection_name :{colleciton_name}')
            print (f'最初の document :{documents[0]}')


def test_ticks_insert_handler():
    hander_obj = TicksInsertHandler()
    print('--------------TickInserHandler def insert_after_processed のテスト---------------')
    yesterday_list = ["20240401", "20240524", "2024/04/30"] 
    for yesterday in yesterday_list:
        hander_obj.insert_after_processed(yesterday)
        # Todo mongodbにインサートする部分と file を取得する部分があるので　それぞれのmockを作るまで実行しない


def test_ticks_takeout_handler():
    takeout_obj = TicksExtractHandler()
    code_str ='9509'
    try:
        takeout_obj.exec(code_str)
    except:
        handle_exception()
    print('--------------TicksExtractHandler def exec のテスト---------------')
    print(f'df head(2): {takeout_obj.df.head(2)}')   
    

if __name__ == '__main__':
    # file_obj = TicksJsonFileInfo()
    # test_ticks_json_file_info(file_obj)
    # test_ticks_insert_to_monogo(file_obj)
    test_ticks_takeout_handler()
    
    
    