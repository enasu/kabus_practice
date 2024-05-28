import asyncio
import websockets
from kabusapi import KabustationApi


async def receive_messages(uri, token):
    # headers = {
    #     "Authorization": token
    # }
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")
            
async def connect_websocket(token):
    push_uri = "ws://host.docker.internal:18081/kabusapi/websocket"
    headers = {
        'Content-Type': 'application/json',
        'Host': 'localhost',
        'X-API-KEY': token  
    }            
    async with websockets.connect(push_uri, extra_headers=headers) as websocket:
        message = '{"data": "Hello World"}'  # 送信するメッセージ
        await websocket.send(message)
        print("Message sent to the server")
        # サーバーからの応答を待ちます
        response = await websocket.recv()
        print("Received from server:", response)        

if __name__ == "__main__":
    obj = KabustationApi(stage="honban")
    token = obj.kabustation_token
    print(f'送信前のtoken :{token}')
    asyncio.get_event_loop().run_until_complete(connect_websocket(token))

