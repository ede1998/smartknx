import asyncio
import websockets
from .converters import *
from .pubsub import RedisConnector
import oyaml as yaml
from threading import Thread
import logging

LOGGER = logging.getLogger(__name__)

_connections = set()
_redis = None
_loop = None

def handle_redis_message(chan, content):
    try:
        # set received data
        ConverterManager.unserialize_binary(chan, content)
    except KeyError:
        return

    json_msg = ConverterManager.serialize_json(chan)
    LOGGER.info('new redis message: %s' % (json_msg,))

    # inform clients about state change
    for websocket in _connections:
        asyncio.create_task(websocket.send(json_msg))


def send_initial_states(websocket):
    for address in ConverterManager.converters.keys():
        asyncio.create_task(websocket.send(ConverterManager.serialize_json(address)))


async def handle_client_message(msg):
    LOGGER.info('new message from a client: %s' % (msg,))
    try:
        group_address, converter = ConverterManager.unserialize_json(msg)
    except KeyError:
        LOGGER.warning('message lead to key error: ' + msg)  
        return
        
    msg = str(converter.bit_size) + ' ' + str(ConverterManager.serialize_binary(group_address))

    await _redis.publish(group_address, msg)


async def ws_handler(websocket, path):
    # Register.
    _connections.add(websocket)
    try:
        LOGGER.info('new connection: %s' % (websocket.remote_address,))
        send_initial_states(websocket)
        async for msg in websocket:
            await handle_client_message(msg)
    except asyncio.CancelledError:
        pass
    finally:
        LOGGER.info('connection closed: %s' % (websocket.remote_address,))
        # Unregister.
        _connections.remove(websocket)
        # Close connection safely
        await websocket.wait_closed()


async def redis_handler():
    global _redis
    _redis = RedisConnector(False)
    await _redis.initialize(handle_redis_message)


async def main():
    global _loop
    _loop = asyncio.get_running_loop()
    with open('../config/network.yaml', 'r') as f:
        config = yaml.safe_load(f)
        ip = config['ws_host']
        port = 8765
    
    # if we don't get a connection to redis, websockets would also return immediately
    # so we need a helper coro, that keeps the loop running
    async def waiter():
        while True:
            await asyncio.sleep(100)

    ws_coro = websockets.serve(ws_handler, ip, port)
    redis_coro = redis_handler()
    waiter_coro = waiter()


    await asyncio.gather(ws_coro, redis_coro, waiter_coro)

def run_in_thread():
    t = Thread(target=asyncio.run, args=[main()])
    t.start()

if __name__ == '__main__':
    asyncio.run(main())
