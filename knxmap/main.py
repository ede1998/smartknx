#!/usr/bin/env python3
import sys

# initialize everything
from data.constants import *
from gateway import *
from messages import *
from targets import *
from exceptions import *


from communicator import KnxCommunicator
from targets import Targets
from misc import setup_logger

# asyncio requires at least Python 3.3
if sys.version_info.major < 3 or \
        (sys.version_info.major > 2 and
         sys.version_info.minor < 3):
    print('At least Python version 3.3 is required to run this script!')
    sys.exit(1)
try:
    # Python 3.4 ships with asyncio in the standard libraries. Users of Python 3.3
    # need to install it, e.g.: pip install asyncio
    import asyncio
except ImportError:
    print('Please install the asyncio module!')
    sys.exit(1)


def start():
    setup_logger(4)
    loop = asyncio.get_event_loop()

    knxcom = KnxCommunicator()
    try:
#             loop.run_until_complete(knxcom.group_writer(
#                 target=args.group_write_address,
#                 value=args.group_write_value))
        loop.run_until_complete(knxcom.monitor(
            targets=Targets('192.168.140.21', 3671).targets,
            group_monitor_mode=True))
    except KeyboardInterrupt:
        for t in asyncio.Task.all_tasks():
            t.cancel()
            try:
                loop.run_until_complete(t)
            except asyncio.CancelledError:
                pass

        if knxcom.bus_protocols:
            # Make sure to send a DISCONNECT_REQUEST
            # when the bus monitor will be closed.
            for p in knxcom.bus_protocols:
                p.knx_tunnel_disconnect()
    finally:
        loop.close()
