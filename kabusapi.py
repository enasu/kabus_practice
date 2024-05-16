import urllib.request
import json
import pprint
import os
import pdb

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
        json_data = json.dumps(params).encode('utf8') if params else ''
        if method == 'GET':
            req = urllib.request.Request('{}?{}'.format(url, urllib.parse.urlencode(params)), method='GET')
        else:   # 'POST' 'PUT' を想定
            #pdb.set_trace()
            req = urllib.request.Request(url, data=json_data, method=method)    
        req.add_header('Content-Type', 'application/json')
        req.add_header('Host', 'localhost')  # `Host` ヘッダーを追加         docker からアクセスするため
        if self.kabustation_token:
            req.add_header('X-API-KEY', self.kabustation_token)

        try:
            with urllib.request.urlopen(req) as res:
                print(res.status, res.reason)
                for header in res.getheaders():
                    print(header)
                print()
                content = json.loads(res.read())
                pprint.pprint(content)
                return content
                
        except urllib.error.HTTPError as e:
            print(e)
            error_content = e.read()  # エラーレスポンスボディを一度変数に格納
            if error_content:  # レスポンスボディが空ではないか確認
                try:
                    content = json.loads(error_content)
                    pprint.pprint(content)
                    return {"error": True,"content":content}
                except json.JSONDecodeError:
                    print("JSON形式ではないエラーレスポンス: ", error_content)
                    return {"error": True, "content": error_content}
            else:
                print("エラーレスポンスボディが空です。")
                return {"error": True, "content": "Empty error response body"}
        except Exception as e:
            print(e)
            return {"error": True, "content": str(e)}
    
    def fetch_token(self):
        endpoint = '/token'
        
        obj = {'APIPassword': self.api_pw}
        # `localhost`を`host.docker.internal`に変更してホストマシンにアクセス       
        content = self._request(endpoint, obj, method='POST')
        if not content['error']:
            self.kabustation_token = content['contents'].get('Token')

    def fetch_orders(self):
        endpoint = '/orders'
        params = { 'product': 0 }               # product - 0:すべて、1:現物、2:信用、3:先物、4:OP
        #params['id'] = '20201207A02N04830518' # id='xxxxxxxxxxxxxxxxxxxx'
        #params['updtime'] = 20240412140000    # updtime=yyyyMMddHHmmss
        #params['details'] =  'false'          # details='true'/'false'
        #params['symbol'] = '9433'             # symbol='xxxx'
        #params['state'] = 5                   # state - 1:待機（発注待機）、2:処理中（発注送信中）、3:処理済（発注済・訂正済）、4:訂正取消送信中、5:終了（発注エラー・取消済・全約定・失効・期限切れ）
        #params['side'] = '2'                  # side - '1':売、'2':買
        #params['cashmargin'] = 3              # cashmargin - 2:新規、3:返済
        
        content = self._request(endpoint, params, method='GET')
        
        return content
    
    def register_symbols(self, symbols):
        endpoint = '/register'
        #symbols は以下の形式
        # symbols = { 'Symbols':
        # [ 
        #    {'Symbol': '9433', 'Exchange': 1},
        #    {'Symbol': '165120018', 'Exchange': 2},
        #    {'Symbol': '145123218', 'Exchange': 2}
        # ] }
        content = self._request(endpoint, symbols, method='PUT')
        pprint.pprint(content)
        
    def unregister(self, symbols):  #登録解除
        endpoint = '/unregister'
        content = self._request(endpoint, symbols, method='PUT')
        pprint.pprint(content)     
        
    def unregister_all(self):
        symbols =[]
        endpoint = '/unregister'
        content = self._request(endpoint, symbols, method='PUT')
        pprint.pprint(content)
        
def reg_symbols():
    symbols = { 'Symbols':
        [
            3778,6301,7201,8354,9509
        ]
        }
    api = KabustationApi(stage='test')
    #response = api.register_symbols(symbols)
    #print(response)
    

if __name__ == '__main__':
    reg_symbols()