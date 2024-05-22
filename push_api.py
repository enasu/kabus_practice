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

if __name__ == "__main__":
    push_uri = "ws://host.docker.internal:18081/kabusapi/websocket"
    obj = KabustationApi(stage="honban")
    token = obj.kabustation_token
    print(f'送信前のtoken :{token}')
    asyncio.get_event_loop().run_until_complete(receive_messages(push_uri, token))

