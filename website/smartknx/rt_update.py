import asyncio
import websockets
import aioredis


async def producer():
    await asyncio.sleep(3)
    return "test"


async def consumer(msg):
    print(msg)


async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)


async def producer_handler(websocket, path):
    while True:
        message = await producer()
        await websocket.send(message)


async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


def main():
    start_server = websockets.serve(handler, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
