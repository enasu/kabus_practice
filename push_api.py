import asyncio
import websockets


symbols=[3778,6146,6301,6526,6857,
         6920,6954,7011,7203,8058,
         8802,9104,9509]

async def receive_messages(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

if __name__ == "__main__":
    push_uri = "ws://localhost:18081/kabuspai/websocket"
    rest_url = 
    asyncio.get_event_loop().run_until_complete(receive_messages(uri))

