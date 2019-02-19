import asyncio
import websockets
from profile_loader.knx_message import KNXMessage
if __name__ == '__main__':
    from pubsub import RedisConnector
else:
    from .pubsub import RedisConnector


_connections = set()
_states = dict()
_redis = None


def handle_redis_message(chan, content):
    print(chan)
    print(content)
    # update _states dict for new clients
    _states[chan] = content

    # inform client about state change
    for websocket in _connections:
        # TODO sensible format
        asyncio.create_task(websocket.send([chan, content]))


def send_initial_states(websocket):
    for entry in _states.items():
        asyncio.create_task(websocket.send(entry))


async def handle_client_message(msg):
    print(msg)
    # TODO send sensible stuff
    await _redis.publish('test', msg)


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
