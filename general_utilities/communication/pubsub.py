import asyncio
import aioredis
import oyaml as yaml
import logging

LOGGER = logging.getLogger(__name__)

class RedisConnector:

    def __init__(self, position_bux_interface=True):
        to_bus_channel = 'smartknx:test:v0:to_bus:'
        from_bus_channel = 'smartknx:test:v0:from_bus:'
        self.sub_channel_prefix = to_bus_channel if position_bux_interface else from_bus_channel
        self.pub_channel_prefix = from_bus_channel if position_bux_interface else to_bus_channel
        self.is_connected = False

    async def create_con_pool(self):
        try:
            with open('../config/network.yaml', 'r') as f:
                config = yaml.safe_load(f)
                url = config['redis']
            self.con_pool = await aioredis.create_redis_pool(url)
            self.is_connected = True
        except OSError as e:
            LOGGER.error(e)

    async def psubscribe(self):
        channels = await self.con_pool.psubscribe(self.sub_channel_prefix + "*")
        self.channel = channels[0]

    def prepare_msg(self, msg):
        channel = msg[0].decode('utf-8')
        content = msg[1].decode('utf-8')

        channel_suffix = channel[len(self.sub_channel_prefix):]
        return channel_suffix, content

    async def receive(self, callback):
        async for msg in self.channel.iter():
            channel, content = self.prepare_msg(msg)
            callback(channel, content)

    async def receive_msg(self):
        msg = await self.channel.get()
        return self.prepare_msg(msg)

    async def publish(self, channel_suffix, text):
        if not self.is_connected:
            return False
        await self.con_pool.publish(self.pub_channel_prefix + channel_suffix, text)

    async def punsubscribe(self):
        await self.con_pool.punsubscribe(self.sub_channel_prefix + "*")

    async def initialize(self, callback):
        await self.create_con_pool()
        if not self.is_connected:
            return False
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
    rc.pub_channel_prefix = "testchannels:"
    rc.sub_channel_prefix = rc.pub_channel_prefix
    await rc.create_con_pool()
    await rc.psubscribe()
    task = asyncio.create_task(rc.receive(process_tuple))
    await rc.publish('test:1', 'my message')
    await rc.publish('test:2', 'better message')
    await rc.punsubscribe()
    await task

if __name__ == '__main__':
    asyncio.run(main())
