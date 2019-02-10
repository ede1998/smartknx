import struct
import logging

from data.constants import KNX_MESSAGE_TYPES
from main import KnxMessage
from tpci import Tpci
from apci import Apci
from cemi import CemiFrame
from emi1 import KnxEmi1Frame
from tp import DataRequest, ExtendedDataRequest
from configuration import KnxDeviceConfigurationRequest, KnxDeviceConfigurationAck
from core import KnxSearchRequest, KnxSearchResponse, KnxDescriptionRequest, \
    KnxDescriptionResponse, KnxConnectRequest, KnxConnectResponse, KnxConnectionStateRequest, \
    KnxConnectionStateResponse, KnxDisconnectRequest, KnxDisconnectResponse
from tunnelling import KnxTunnellingRequest, KnxTunnellingAck
from routing import KnxRoutingIndication, KnxRoutingLostMessage, KnxRoutingBusy
from remconf import KnxRemoteDiagnosticRequest, KnxRemoteDiagnosticResponse

LOGGER = logging.getLogger(__name__)


def parse_message(data):
    """
    Determines the message type of data and returns a corresponding class instance. This is a helper
    function for data that has been received from a KNXnet/IP gateway.

    :param data: Incoming data from a KNXnet/IP gateway.
    :return: A class instance of any KnxMessage subclass or None if data is not a valid KNX message.
    """
    try:
        _, _, message_type = struct.unpack('>BBH', data[:4])
        message_type = int(message_type)
    except struct.error as e:
        LOGGER.exception(e)
        return
    except ValueError as e:
        LOGGER.exception(e)
        return

    if message_type == KNX_MESSAGE_TYPES.get('SEARCH_RESPONSE'):
        LOGGER.debug('Parsing KnxSearchResponse')
        return KnxSearchResponse(data)
    elif message_type == KNX_MESSAGE_TYPES.get('DESCRIPTION_RESPONSE'):
        LOGGER.debug('Parsing KnxDescriptionResponse')
        return KnxDescriptionResponse(data)
    elif message_type == KNX_MESSAGE_TYPES.get('CONNECT_RESPONSE'):
        LOGGER.debug('Parsing KnxConnectResponse')
        return KnxConnectResponse(data)
    elif message_type == KNX_MESSAGE_TYPES.get('TUNNELLING_REQUEST'):
        LOGGER.debug('Parsing KnxTunnellingRequest')
        return KnxTunnellingRequest(data)
    elif message_type == KNX_MESSAGE_TYPES.get('TUNNELLING_ACK'):
        LOGGER.debug('Parsing KnxTunnelingAck')
        return KnxTunnellingAck(data)
    elif message_type == KNX_MESSAGE_TYPES.get('CONNECTIONSTATE_REQUEST'):
        LOGGER.debug('Parsing KnxConnectionStateRequest')
        return KnxConnectionStateRequest(data)
    elif message_type == KNX_MESSAGE_TYPES.get('CONNECTIONSTATE_RESPONSE'):
        LOGGER.debug('Parsing KnxConnectionStateResponse')
        return KnxConnectionStateResponse(data)
    elif message_type == KNX_MESSAGE_TYPES.get('DISCONNECT_REQUEST'):
        LOGGER.debug('Parsing KnxDisconnectRequest')
        return KnxDisconnectRequest(data)
    elif message_type == KNX_MESSAGE_TYPES.get('DISCONNECT_RESPONSE'):
        LOGGER.debug('Parsing KnxDisconnectResponse')
        return KnxDisconnectResponse(data)
    elif message_type == KNX_MESSAGE_TYPES.get('DEVICE_CONFIGURATION_REQUEST'):
        LOGGER.debug('Parsing KnxDeviceConfigurationRequest')
        return KnxDeviceConfigurationRequest(data)
    elif message_type == KNX_MESSAGE_TYPES.get('DEVICE_CONFIGURATION_RESPONSE'):
        LOGGER.debug('Parsing KnxDeviceConfigurationAck')
        return KnxDeviceConfigurationAck(data)
    else:
        LOGGER.error('Unknown message type: {}'.format(message_type))
        return None