from codes import *
from EventBus import EventBus

encode_simple_utf = (
    FILLER_OPCODE,
    NAME_OPCODE,
    CONNECT_TO_SERVER_MEDIATED_OPCODE,
    CONNECT_TO_P2P_OPCODE,
    CLIENT_REQUEST_P2P_OPCODE,
    )

encode_format_json_ipv4_address = (
    RESPONSE_CLIENT_ADDRESS_OPCODE,
    )

encode_format_json_p2p_request = (
    CONSENT_TO_P2P,
    )

encode_pickle = (
    RESPONSE_ENCRYPTION_METHODS_OPCODE,
    RESPONSE_USER_LIST_OPCODE
)

ENCODERS = {
    # IP address JSON encoding format
    frozenset({
        encode_format_json_ipv4_address: EventBus.encode_format_json_ipv4_address,
        encode_format_json_p2p_request: EventBus.encode_format_json_p2p_request,
        encode_simple_utf: EventBus.encode_simple_utf,
        encode_pickle: EventBus.encode_pickle,
    })
}