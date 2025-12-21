from codes import *
from codec.encoders import *
from codec.decoders import *

OPCODE_simple_utf = (
    FILLER_OPCODE,
    NAME_OPCODE,
    RESPONSE_NAME_OPCODE,
    REQUEST_USER_LIST_OPCODE,
    CONNECT_TO_SERVER_MEDIATED_OPCODE,
    CONNECT_TO_P2P_OPCODE,
    CLIENT_REQUEST_P2P_OPCODE,
    CONSENT_REQUEST_P2P_OPCODE,
    )

OPCODE_format_json_ipv4_address = (
    RESPONSE_CLIENT_ADDRESS_OPCODE,
    )

OPCODE_format_json_p2p_request = (
    CONSENT_TO_P2P,
    CONNECT_TO_P2P_OPCODE,
    )

OPCODE_pickle = (
    RESPONSE_ENCRYPTION_METHODS_OPCODE,
    RESPONSE_USER_LIST_OPCODE
)

ENCODER_GROUPS = {
    OPCODE_format_json_ipv4_address: encode_format_json_ipv4_address,
    OPCODE_format_json_p2p_request: encode_format_json_p2p_request,
    OPCODE_simple_utf: encode_simple_utf,
    OPCODE_pickle: encode_pickle,

}

DECODER_GROUPS = {
        OPCODE_simple_utf: decode_simple_utf,
        OPCODE_pickle: decode_pickle_numbered_list,
        OPCODE_format_json_ipv4_address: decode_format_json_ipv4_address,
        OPCODE_format_json_p2p_request: decode_format_json_p2p,
}

ENCODERS = {
    opcode: encoder
    for opcodes, encoder in ENCODER_GROUPS.items()
    for opcode in opcodes
}
DECODERS = {
    opcode: decoder
    for opcodes, decoder in DECODER_GROUPS.items()
    for opcode in opcodes
}