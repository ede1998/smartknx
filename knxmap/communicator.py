import asyncio
import codecs
import collections
import functools
import logging
import socket
import struct
import time

try:
    # Python 3.4
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5 renamed it to Queue
    from asyncio import Queue

import utils
from data.constants import *
from messages import CemiFrame, KnxDescriptionResponse, KnxEmi1Frame
from gateway import *
from targets import *
from exceptions import *
from bus.tunnel import KnxTunnelConnection
from bus.router import KnxRoutingConnection
from bus.monitor import KnxBusMonitor

LOGGER = logging.getLogger(__name__)

try:
    import hid
    USB_SUPPORT = True
except ImportError:
    USB_SUPPORT = False


class KnxCommunicator(object):
    def __init__(self, targets=None, loop=None, configuration_reads=True,
                 bus_timeout=2, iface=False, nat_mode=False):
        self.loop = loop or asyncio.get_event_loop()
        # q contains all KNXnet/IP gateways
        self.q = Queue(loop=self.loop)
        # bus_protocols is a list of all bus protocol instances for proper connection shutdown
        self.bus_protocols = []
        # knx_gateways is a list of KnxTargetReport objects, one for each found KNXnet/IP gateway
        self.knx_gateways = []
        self.t0 = time.time()
        self.t1 = None
        self.desc_timeout = None
        self.desc_retries = None
        self.knx_source = None
        self.configuration_reads = configuration_reads
        self.bus_timeout = bus_timeout
        self.iface = iface
        self.nat_mode = nat_mode
        if targets:
            self.set_targets(targets)
        else:
            self.targets = set()

    def set_targets(self, targets):
        self.targets = targets
        for target in self.targets:
            self.add_target(target)

    def add_target(self, target):
        self.q.put_nowait(target)

    @asyncio.coroutine
    def _knx_description_worker(self):
        """Send a KnxDescription request to see if target is a KNX device."""
        try:
            while True:
                target = self.q.get_nowait()
                LOGGER.debug('Scanning {}'.format(target))
                response = None
                for _try in range(self.desc_retries):
                    LOGGER.debug('Sending {}. KnxDescriptionRequest to {}'.format(_try, target))
                    future = asyncio.Future()
                    yield from self.loop.create_datagram_endpoint(
                        functools.partial(KnxGatewayDescription, future,
                                          timeout=self.desc_timeout, nat_mode=self.nat_mode),
                        remote_addr=target)
                    response = yield from future
                    if response:
                        break

                if response and isinstance(response, KnxDescriptionResponse):
                    target_report = KnxTargetReport(
                        host=target[0],
                        port=target[1],
                        mac_address=response.dib_dev_info.get('knx_mac_address'),
                        knx_address=response.dib_dev_info.get('knx_address'),
                        device_serial=response.dib_dev_info.get('knx_device_serial'),
                        friendly_name=response.dib_dev_info.get('device_friendly_name'),
                        device_status=response.dib_dev_info.get('device_status'),
                        knx_medium=response.dib_dev_info.get('knx_medium'),
                        project_install_identifier=response.dib_dev_info.get('project_install_identifier'),
                        supported_services=[
                            KNX_SERVICES[k] for k, v in
                            response.dib_supp_sv_families.get('families').items()],
                        bus_devices=[])

                    # TODO: should we check if the device announces support? (support is mandatory)
                    if self.configuration_reads:
                        # Try to create a DEVICE_MGMT_CONNECTION connection
                        future = asyncio.Future()
                        transport, bus_protocol = yield from self.loop.create_datagram_endpoint(
                            functools.partial(
                                KnxTunnelConnection,
                                future,
                                connection_type=_CONNECTION_TYPES.get('DEVICE_MGMT_CONNECTION'),
                                ndp_defer_time=self.bus_timeout,
                                knx_source=self.knx_source,
                                nat_mode=self.nat_mode),
                            remote_addr=target)
                        self.bus_protocols.append(bus_protocol)
                        # Make sure the tunnel has been established
                        connected = yield from future
                        if connected:
                            configuration = collections.OrderedDict()
                            # Read additional individual addresses
                            count = yield from bus_protocol.configuration_request(
                                        target,
                                        object_type=11,
                                        start_index=0,
                                        property=OBJECTS.get(11).get('PID_ADDITIONAL_INDIVIDUAL_ADDRESSES'))
                            if count and count.data:
                                count = int.from_bytes(count.data, 'big')
                                conf_response = yield from bus_protocol.configuration_request(
                                        target,
                                        object_type=11,
                                        num_elements=count,
                                        property=OBJECTS.get(11).get('PID_ADDITIONAL_INDIVIDUAL_ADDRESSES'))
                                if conf_response and conf_response.data:
                                    data = conf_response.data
                                    target_report.additional_individual_addresses = []
                                    for addr in [data[i:i+2] for i in range(0, len(data), 2)]:
                                        target_report.additional_individual_addresses.append(
                                            knxmap.utils.parse_knx_address(int.from_bytes(addr, 'big')))

                            # Read manufacurer ID
                            count = yield from bus_protocol.configuration_request(
                                        target,
                                        object_type=0,
                                        start_index=0,
                                        property=OBJECTS.get(0).get('PID_MANUFACTURER_ID'))
                            if count and count.data:
                                count = int.from_bytes(count.data, 'big')
                                conf_response = yield from bus_protocol.configuration_request(
                                        target,
                                        object_type=0,
                                        num_elements=count,
                                        property=OBJECTS.get(0).get('PID_MANUFACTURER_ID'))
                                if conf_response and conf_response.data:
                                    target_report.manufacturer = knxmap.utils.get_manufacturer_by_id(
                                        int.from_bytes(conf_response.data, 'big'))

                            # TODO: do more precise checks what to extract and add it to the target report
                            # for k, v in OBJECTS.get(11).items():
                            #     count = yield from bus_protocol.configuration_request(target,
                            #                                                           object_type=11,
                            #                                                           start_index=0,
                            #                                                           property=v)
                            #     if count and count.data:
                            #         count = int.from_bytes(count.data, 'big')
                            #     else:
                            #         continue
                            #     conf_response = yield from bus_protocol.configuration_request(target,
                            #                                                                   object_type=11,
                            #                                                                   num_elements=count,
                            #                                                                   property=v)
                            #     if conf_response and conf_response.data:
                            #
                            #         print(k + ':')
                            #         print(conf_response.data)

                            bus_protocol.knx_tunnel_disconnect()

                    # TODO: at the end, add alive gateways to this list
                    self.knx_gateways.append(target_report)
                self.q.task_done()
        except (asyncio.CancelledError, asyncio.QueueEmpty):
            pass

    @asyncio.coroutine
    def monitor(self, targets=None, group_monitor_mode=False):
        if targets:
            self.set_targets(targets)
        if group_monitor_mode:
            LOGGER.debug('Starting group monitor')
        else:
            LOGGER.debug('Starting bus monitor')
        future = asyncio.Future()
        transport, protocol = yield from self.loop.create_datagram_endpoint(
            functools.partial(KnxBusMonitor, future, group_monitor=group_monitor_mode),
            remote_addr=list(self.targets)[0])
        self.bus_protocols.append(protocol)
        LOGGER.debug('here i am')
        yield from future

    @asyncio.coroutine
    def group_writer(self, target, value=0, routing=False, desc_timeout=2,
                     desc_retries=2, iface=False):
        self.desc_timeout = desc_timeout
        self.desc_retries = desc_retries
        self.iface = iface
        workers = [asyncio.Task(self._knx_description_worker(), loop=self.loop)
                   for _ in range(self.max_workers if len(self.targets) > self.max_workers else len(self.targets))]
        self.t0 = time.time()
        yield from self.q.join()
        self.t1 = time.time()
        for w in workers:
            w.cancel()

        if self.knx_gateways:
            # TODO: make sure only a single gateway is supplied
            knx_gateway = self.knx_gateways[0]
        else:
            LOGGER.error('No valid KNX gateway found')
            return
        
        if True:
            # Use KNX Tunnelling to write group values
            if 'KNXnet/IP Tunnelling' not in knx_gateway.supported_services:
                LOGGER.error('KNX gateway {gateway} does not support Tunneling'.format(
                    gateway=knx_gateway.host))
            future = asyncio.Future()
            transport, protocol = yield from self.loop.create_datagram_endpoint(
                functools.partial(KnxTunnelConnection, future, nat_mode=self.nat_mode),
                remote_addr=(knx_gateway.host, knx_gateway.port))
            self.bus_protocols.append(protocol)
            # Make sure the tunnel has been established
            connected = yield from future
            if connected:
                # TODO: what if we have devices that access more advanced payloads?
                if isinstance(value, str):
                    value = int(value)
                yield from protocol.apci_group_value_write(target, value=value)
                protocol.knx_tunnel_disconnect()