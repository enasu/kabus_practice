import urllib.request
import json
import pprint
import os
import pdb
from utility import time_it, handle_exception

class KabustationApi:
    def __init__(self, stage='test'):
        self.kabustation_token=''
        if stage =="honban":
            self.baseurl='http://host.docker.internal:18080/kabusapi'
            self.api_pw = os.environ.get('KABUSTATION_API_PW')
        else:
            self.baseurl='http://host.docker.internal:18081/kabusapi' 
            self.api_pw = os.environ.get('KABUSTATION_API_TEST_PW')
        self.fetch_token()

    def _request(self, endpoint, params=None, method='GET'):
        url=self.baseurl + endpoint
        json_data = json.dumps(params).encode('utf8') if params else None
        if method == 'GET':
            if params:
                req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
            else:
                req = urllib.request.Request(url, method='GET')

        else:   # 'POST' 'PUT' を想定
            req = urllib.request.Request(url, data=json_data, method=method)    
        req.add_header('Content-Type', 'application/json')
        req.add_header('Host', 'localhost')  # `Host` ヘッダーを追加         docker からアクセスするため
    
        if self.kabustation_token:
            req.add_header('X-API-KEY', self.kabustation_token)

        try:
            with urllib.request.urlopen(req) as res:
                status_code = res.getcode()
                content = res.read()
                print("token Status Code:", status_code)
                #print("Response Contnt:", content)
                
                #print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                content = json.loads(content)
                return content
                
        except urllib.error.HTTPError as e:
            print(e)
            error_content = e.read()  # エラーレスポンスボディを一度変数に格納
            if error_content:  # レスポンスボディが空ではないか確認
                try:
                    content = json.loads(error_content)
                    pprint.pprint(content)
                    return content
                except json.JSONDecodeError:
                    print("JSON形式ではないエラーレスポンス: ", error_content)
                    return error_content
            else:
                print("エラーレスポンスボディが空です。")
                return  "Empty error response body"
        except Exception:
            handle_exception()
            return  str(e)
    
    def fetch_token(self):
        endpoint = '/token'
        
        obj = {'APIPassword': self.api_pw}
        # `localhost`を`host.docker.internal`に変更してホストマシンにアクセス       
        content = self._request(endpoint, obj, method='POST')

        self.kabustation_token = content['Token']
    @time_it
    def fetch_orders(self, params = { 'product': 0, 'state':5}):
        endpoint = '/orders'
        #params = { 'product': 0 }               # product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        #params['id'] = '20201207A02N04830518' # id='xxxxxxxxxxxxxxxxxxxx'
        #params['updtime'] = 20240412140000    # updtime=yyyyMMddHHmmss
        #params['details'] =  'false'          # details='true'/'false'
        #params['symbol'] = '9433'             # symbol='xxxx'
        #params['state'] = 5                   # state - 1:待機（発注待機）、2:処理中（発注送信中）、3:処理済（発注済・訂正済）、4:訂正取消送信中、5:終了（発注エラー・取消済・全約定・失効・期限切れ）
        #params['side'] = '2'                  # side - '1':売、'2':買
        #params['cashmargin'] = 3              # cashmargin - 2:新規、3:返済

        try:        
            content = self._request(endpoint, params=params, method='GET')    
            return content
        except Exception:
            handle_exception()
            raise
    def register_symbols(self, symbols):
        endpoint = '/register'
        #symbols は以下の形式
        # symbols = { 'Symbols':
        # [ 
        #    {'Symbol': '9433', 'Exchange': 1},
        #    {'Symbol': '165120018', 'Exchange': 2},
        #    {'Symbol': '145123218', 'Exchange': 2}
        # ] }
        symbols_data = self.synbols_dict(symbols)
        #pdb.set_trace()
        content = self._request(endpoint, params=symbols_data, method='PUT')
        pprint.pprint(content)
        
    def synbols_dict(self,symbols):
        symbol_list = []
        for symbol in symbols:
            symbol_list += [{'Symbol': symbol, "Exchange": 1,}]     #Exchange :1 は東証
        data = { "Symbols": symbol_list}
        return data
        
    def unregister(self, symbols):  #登録解除
        endpoint = '/unregister'
        symbols_data = self.synbols_dict(symbols)
 
        content = self._request(endpoint, params=symbols_data, method='PUT')
        pprint.pprint(content)
        
        
    def unregister_all(self):
        endpoint = '/unregister/all'
        content = self._request(endpoint, params=None, method='PUT')
        pprint.pprint(content)
        
def reg_symbols(stage='test'):
    symbols=[9509]

    api = KabustationApi(stage=stage)
    response = api.register_symbols(symbols)
    print(response)

@time_it
def fetch_orders(updtime,stage='test'):
    params = { 
              'product': 0,
              'updtime':updtime
              }
    api = KabustationApi(stage= stage)
    data = api.fetch_orders(params=params)



def unregister_all(stage='test'):
    api = KabustationApi(stage= stage)
    response = api.unregister_all()
    print(response)
    
def unregister(stage='test'):
    symbols=[6301,6526,6857,
            6920,6954,7011,7203,8058]
    api = KabustationApi(stage= stage)
    response = api.unregister(symbols)
    print(response)


from datetime import datetime
from mongodb import MongoDBManager

if __name__ == '__main__':
    #updtime = 20240517140000
    #fetch_orders(updtime, stage='honban')
   #unregister_all(stage="honban")
   #reg_symbols("honban")
   #unregister(stage="honban")
   
    dt_now = datetime.now()
    today_str = dt_now.strftime('%Y%m%d') 
    today = datetime.strptime(today_str, '%Y%m%d')
    today_microsec= int(today.timestamp() * 1_000_000) 
    print(today_microsec)
    params={
        'product': 0 ,
        'updtime': today_microsec,
        'state':5
    }
    kabustation_api = KabustationApi(stage='honban')
    api_datas = kabustation_api.fetch_orders(params=params)
    kabusdb = MongoDBManager('stock_kabu',collection_name='orders')
    # アップサートのキーを定義
    upsert_key = ['ID']
    kabusdb.insert_upsert(api_datas, upsert_key)