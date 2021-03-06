import logging
import codecs
import functools
import asyncio
from ..general_utilities.communication.pubsub import RedisConnector
import sys

from knx.bus.tunnel import KnxTunnelConnection
from knx.data.constants import *
from knx.messages import parse_message, KnxConnectRequest, KnxConnectResponse, \
                            KnxTunnellingRequest, KnxTunnellingAck, KnxConnectionStateResponse, \
                            KnxDisconnectRequest, KnxDisconnectResponse


LOGGER = logging.getLogger(__name__)


class KnxBusMonitor(KnxTunnelConnection):
    """Implementation of bus_monitor_mode and group_monitor_mode."""
    def __init__(self, future, loop=None, group_monitor=True):
        super(KnxBusMonitor, self).__init__(future, loop=loop)
        self.group_monitor = group_monitor
        self.redis = None
        self.sequence_counter_incoming = -1

    def connection_made(self, transport):
        LOGGER.debug('Connection opened to knx gateway')
        self.transport = transport
        self.peername = self.transport.get_extra_info('peername')
        self.sockname = self.transport.get_extra_info('sockname')
        if self.group_monitor:
            # Create a TUNNEL_LINKLAYER layer request (default)
            connect_request = KnxConnectRequest(sockname=self.sockname)
        else:
            # Create a TUNNEL_BUSMONITOR layer request
            connect_request = KnxConnectRequest(sockname=self.sockname,
                                                layer_type='TUNNEL_BUSMONITOR')
        LOGGER.trace_outgoing(connect_request)
        self.transport.sendto(connect_request.get_message())
        # Send CONNECTIONSTATE_REQUEST to keep the connection alive
        self.loop.call_later(50, self.knx_keep_alive)
    
    def send_message(self, group, value):
        values = value.split(' ', 1)
        size = int(values[0])
        value = int(values[1])
        asyncio.create_task(self.apci_group_value_write(group, value=value, size=size))

    def subscribe_to_redis(self):
        self.redis = RedisConnector()
        asyncio.create_task(self.redis.initialize(self.send_message))
    
    def publish_to_redis(self, message):
        if not isinstance(message, KnxTunnellingRequest):
            return
        cemi = tpci = apci= {}
        if message.cemi:
            cemi = message.cemi
            if cemi.tpci:
                tpci = cemi.tpci
                if cemi.apci:
                    apci = cemi.apci

        if not (cemi.knx_destination and cemi.extended_control_field and \
                cemi.extended_control_field.get('address_type')):
            return
        
        if self.sequence_counter_incoming >= 255:
            self.sequence_counter_incoming = -1
        if message.sequence_counter <= self.sequence_counter_incoming:
            return
        
        self.sequence_counter_incoming = message.sequence_counter

        dst_addr = message.parse_knx_group_address(cemi.knx_destination)
        data = apci.apci_data
        
        asyncio.create_task(self.redis.publish(dst_addr, str(data)))
    
    def datagram_received(self, data, addr):
        knx_message = parse_message(data)
        if not knx_message:
            LOGGER.error('Invalid KNX message: {}'.format(data))
            self.knx_tunnel_disconnect()
            self.transport.close()
            self.future.set_result(None)
            return
        knx_message.set_peer(addr)
        LOGGER.trace_incoming(knx_message)
        if isinstance(knx_message, KnxConnectResponse):
            if not knx_message.ERROR:
                if not self.tunnel_established:
                    self.tunnel_established = True
                self.communication_channel = knx_message.communication_channel
                self.knx_source_address = knx_message.data_block.get('knx_address')
                # subscribe to channels
                self.subscribe_to_redis()
            else:
                if not self.group_monitor and knx_message.ERROR_CODE == 0x23:
                    LOGGER.error('Device does not support BUSMONITOR, try --group-monitor instead')
                else:
                    LOGGER.error('Connection setup error: {}'.format(knx_message.ERROR))
                self.transport.close()
                self.future.set_result(None)
        elif isinstance(knx_message, KnxTunnellingRequest):
            self.print_message(knx_message)
            if CEMI_PRIMITIVES[knx_message.cemi.message_code] == 'L_Data.con' or \
                    CEMI_PRIMITIVES[knx_message.cemi.message_code] == 'L_Data.ind' or \
                    CEMI_PRIMITIVES[knx_message.cemi.message_code] == 'L_Busmon.ind':
                tunnelling_ack = KnxTunnellingAck(
                    communication_channel=knx_message.communication_channel,
                    sequence_count=knx_message.sequence_counter)
                LOGGER.trace_outgoing(tunnelling_ack)
                # publish to redis
                self.publish_to_redis(knx_message)
        elif isinstance(knx_message, KnxTunnellingAck):
            self.print_message(knx_message)
        elif isinstance(knx_message, KnxConnectionStateResponse):
            # After receiving a CONNECTIONSTATE_RESPONSE schedule the next one
            self.loop.call_later(50, self.knx_keep_alive)
        elif isinstance(knx_message, KnxDisconnectRequest):
            connect_response = KnxDisconnectResponse(communication_channel=self.communication_channel)
            self.transport.sendto(connect_response.get_message())
            self.transport.close()
            self.future.set_result(None)
        elif isinstance(knx_message, KnxDisconnectResponse):
            self.transport.close()
            self.future.set_result(None)

    def print_message(self, message):
        """A generic message printing function. It defines
        a format for the monitoring modes."""
        if not isinstance(message, KnxTunnellingRequest):
            return
        assert isinstance(message, KnxTunnellingRequest)
        cemi = tpci = apci= {}
        if message.cemi:
            cemi = message.cemi
            if cemi.tpci:
                tpci = cemi.tpci
                if cemi.apci:
                    apci = cemi.apci
        if cemi.knx_destination and cemi.extended_control_field and \
                cemi.extended_control_field.get('address_type'):
            dst_addr = message.parse_knx_group_address(cemi.knx_destination)
        elif cemi.knx_destination:
            dst_addr = message.parse_knx_address(cemi.knx_destination)
        format = ('[chan_id:{chan_id},seq_no:{seq_no},message_code:{msg_code},'
                  'source_addr:{src_addr},dest_addr:{dst_addr},tpci_type:{tpci_type},'
                  'tpci_seq:{tpci_seq},apci_type:{apci_type},apci_data:{apci_data}]').format(
            chan_id=message.communication_channel,
            seq_no=message.sequence_counter,
            msg_code=CEMI_PRIMITIVES.get(cemi.message_code),
            src_addr=message.parse_knx_address(cemi.knx_source),
            dst_addr=dst_addr,
            tpci_type=_CEMI_TPCI_TYPES.get(tpci.tpci_type),
            tpci_seq=tpci.sequence,
            apci_type=_CEMI_APCI_TYPES.get(apci.apci_type),
            apci_data=apci.apci_data)
        LOGGER.info(format)
