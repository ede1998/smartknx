import asyncio
import websockets
if __name__ == '__main__':
    from pubsub import RedisConnector
else:
    from .pubsub import RedisConnector


class WebsocketHandler:

    def  __init__(self, redis):
        self.redis = redis

    async def initialize(self):
        await self.redis.create_con_pool()
        await self.redis.psubscribe()

    async def consumer_handler(self, websocket, path):
        async for msg in websocket:
            print(msg)
            # send to redis
            await self.redis.publish('13/1/0', msg)

    async def producer_handler(self, websocket, path):
        while True:
            # receive from redis
            channel, msg = await self.redis.receive_msg()
            print(channel)
            print(msg)
            # TODO save to dict?
            # TODO update websocket


    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


def main():
    redis = RedisConnector(False)

    ws_handler = WebsocketHandler(redis)
    start_server = websockets.serve(ws_handler.handler, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(ws_handler.initialize())
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
