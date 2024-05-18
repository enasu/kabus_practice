import asyncio
import websockets

async def receive_messages(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

if __name__ == "__main__":
    push_uri = "ws://host.docker.internal:18081/kabuspai/websocket"
    asyncio.get_event_loop().run_until_complete(receive_messages(push_uri))

