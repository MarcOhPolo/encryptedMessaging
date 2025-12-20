OPCODE_PREFIX = "op"

# Define opcodes
# First digit, direction of communication, 0 = client to server (recieved), 1 = server to client (sent)
# Second digit, type of encoder/decoder, 0 default(utf-8), 1= pickle object, 2 = json
# Third digit, subject of communication, 000=filler content, 001 = name registration, 002 = user list, 003 = connect to server mediated, 004 = connect to p2p, 005 = client request p2p,
# 006 = consent request p2p

POSITION_OF_DATA_FLOW = -3  # Position of data flow digit in opcode
POSITION_OF_ENCODING_TYPE = -2  # Position of encoding digit in opcode
POSITION_OF_SUBJECT = -1  # Position of subject digit in opcode


FILLER_OPCODE = OPCODE_PREFIX+"000"
NAME_OPCODE = OPCODE_PREFIX+"001"
CONNECT_TO_SERVER_MEDIATED_OPCODE = OPCODE_PREFIX+"003"
CONNECT_TO_P2P_OPCODE = OPCODE_PREFIX+"004"
CLIENT_REQUEST_P2P_OPCODE = OPCODE_PREFIX+"005"
CONSENT_TO_P2P = OPCODE_PREFIX+"027"
REQUEST_USER_LIST_OPCODE = OPCODE_PREFIX+"002"
RESPONSE_USER_LIST_OPCODE = OPCODE_PREFIX+"112"
RESPONSE_ENCRYPTION_METHODS_OPCODE = OPCODE_PREFIX+"119"
RESPONSE_NAME_OPCODE = OPCODE_PREFIX+"101"
RESPONSE_CLIENT_ADDRESS_OPCODE = OPCODE_PREFIX+"124"
CONSENT_REQUEST_P2P_OPCODE = OPCODE_PREFIX+"107"

opcode_length = len(FILLER_OPCODE)

#Temporary, will make better way than manual filling of this group
server_to_client_group = (
    RESPONSE_USER_LIST_OPCODE,
    RESPONSE_ENCRYPTION_METHODS_OPCODE,
    RESPONSE_NAME_OPCODE,
    RESPONSE_CLIENT_ADDRESS_OPCODE,
    CONSENT_REQUEST_P2P_OPCODE
)

