import asyncio
import websockets
from profile_loader.knx_message import KNXMessage, Type
from .pubsub import RedisConnector
import oyaml as yaml
from threading import Thread

_connections = set()
_redis = None
_loop = None

def handle_redis_message(chan, content):
    # dict with last msgs for new clients is automatically updated
    knxmsg = KNXMessage.unserialize_redis(chan, content, KNXMessage.get_group_type(chan))

    # inform client about state change
    for websocket in _connections:
        asyncio.create_task(websocket.send(knxmsg.serialize_json()))


def send_initial_states(websocket):
    for entry in KNXMessage.group_address_translator.values():
        if not entry.data is None:
            asyncio.create_task(websocket.send(entry.serialize_json()))


async def handle_client_message(msg):
    knxmsg = KNXMessage.unserialize_json(msg)
    if knxmsg is None:
        return
    print(knxmsg)

    channel, msg = knxmsg.serialize_redis()

    await _redis.publish(channel, str(msg))


async def ws_handler(websocket, path):
    # Register.
    _connections.add(websocket)
    try:
        send_initial_states(websocket)
        async for msg in websocket:
            await handle_client_message(msg)
    except asyncio.CancelledError:
        pass
    finally:
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
    ws_coro = websockets.serve(ws_handler, ip, port)
    redis_coro = redis_handler()

    await asyncio.gather(ws_coro, redis_coro)

def run_in_thread():
    t = Thread(target=asyncio.run, args=[main()])
    t.start()

if __name__ == '__main__':
    asyncio.run(main())
