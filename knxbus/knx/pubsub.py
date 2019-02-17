import asyncio
import aioredis


class RedisConnector:

    async def create_con_pool(self):
        self.con_pool = await aioredis.create_redis_pool('redis://localhost')

    async def psubscribe(self, channel):
       channels = await self.con_pool.psubscribe(channel)
       self.channel = channels[0]

    async def receive(self, callback):
       async for msg in self.channel.iter():
           callback(msg)

    async def publish(self, channel, text):
       await self.con_pool.publish(channel, text)

    async def punsubscribe(self, channel):
       await self.con_pool.punsubscribe(channel)
    
    async def initialize(self, channel_pattern, callback):
        await self.create_con_pool()
        await self.psubscribe(channel_pattern)
        await self.receive(callback)

def process_tuple(t):
    print(type(t))
    print(t[0])
    print(t[1])

async def main():
    rc = RedisConnector()
    await rc.create_con_pool()
    await rc.psubscribe('test:*')
    task = asyncio.create_task(rc.receive(process_tuple))
    await rc.publish('test:1', 'my message')
    await rc.publish('test:2', 'better message')
    await rc.punsubscribe('test:*')
    await task

if __name__ == '__main__':
    asyncio.run(main())
    