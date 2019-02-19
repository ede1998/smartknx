import asyncio
import websockets
from profile_loader.knx_message import KNXMessage, Type
if __name__ == '__main__':
    from pubsub import RedisConnector
else:
    from .pubsub import RedisConnector


_connections = set()
_states = dict()
_redis = None


def handle_redis_message(chan, content):
    knxmsg = KNXMessage.unserialize_redis(chan, content, KNXMessage.group_address_translator.get(chan, Type.UNKOWN))
    
    print(chan)
    print(content)
    # update _states dict for new clients
    _states[chan] = content

    # inform client about state change
    for websocket in _connections:
        asyncio.create_task(websocket.send(knxmsg.serialize_json()))


def send_initial_states(websocket):
    for entry in _states.items():
        asyncio.create_task(websocket.send(entry))


async def handle_client_message(msg):
    knxmsg = KNXMessage.unserialize_json(msg)
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
    ws_coro = websockets.serve(ws_handler, 'localhost', 8765)
    redis_coro = redis_handler()

    await asyncio.gather(ws_coro, redis_coro)


if __name__ == '__main__':
    asyncio.run(main())
