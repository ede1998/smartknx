import asyncio
import aioredis



class RedisConnector:

    def __init__(self):
        self.to_bus_channel = 'smartknx:test:v0:to_bus:'
        self.from_bus_channel = 'smartknx:test:v0:from_bus:'

    async def create_con_pool(self):
        self.con_pool = await aioredis.create_redis_pool('redis://localhost')

    async def psubscribe(self):
       channels = await self.con_pool.psubscribe(self.to_bus_channel + "*")
       self.channel = channels[0]

    async def receive(self, callback):
       async for msg in self.channel.iter():
           channel = msg[0].decode('utf-8')
           content = msg[1].decode('utf-8')

           channel_suffix = channel[len(self.to_bus_channel):]
           callback(channel_suffix, content)

    async def publish(self, channel_suffix, text):
       await self.con_pool.publish(self.from_bus_channel + channel_suffix, text)

    async def punsubscribe(self):
       await self.con_pool.punsubscribe(self.to_bus_channel + "*")
    
    async def initialize(self, callback):
        await self.create_con_pool()
        await self.psubscribe()
        await self.receive(callback)
        await self.punsubscribe()

def process_tuple(t):
    print(type(t))
    print(type(t[0]))
    print(type(t[1]))
    print(t[0])
    print(t[1])

async def main():
    rc = RedisConnector()
    rc.from_bus_channel = "testchannels:"
    rc.to_bus_channel = rc.from_bus_channel
    await rc.create_con_pool()
    await rc.psubscribe()
    task = asyncio.create_task(rc.receive(process_tuple))
    await rc.publish('test:1', 'my message')
    await rc.publish('test:2', 'better message')
    await rc.punsubscribe()
    await task

if __name__ == '__main__':
    asyncio.run(main())
    