from queue import Queue
import pickle
import json

class codes:
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

    RESPONSE_USER_LIST_OPCODE = OPCODE_PREFIX+"112"
    RESPONSE_ENCRYPTION_METHODS_OPCODE = OPCODE_PREFIX+"119"
    RESPONSE_NAME_OPCODE = OPCODE_PREFIX+"101"
    REQUEST_USER_LIST_OPCODE = OPCODE_PREFIX+"002"
    RESPONSE_CLIENT_ADDRESS_OPCODE = OPCODE_PREFIX+"124"
    CONSENT_REQUEST_P2P_OPCODE = OPCODE_PREFIX+"107"

    ENCODING_TYPE_ADDRESS_JSON = {RESPONSE_CLIENT_ADDRESS_OPCODE[POSITION_OF_SUBJECT]}  # JSON encoded ip,port format

    opcode_length = len(FILLER_OPCODE)  # All opcodes are the same length

class EventBus:

    # Initialize queues for each opcode that requires event handling
    _queues = {
        code: Queue()
        for code in codes.__dict__.values()
        if isinstance(code, str) and len(code) >= 3 and code[codes.POSITION_OF_DATA_FLOW] == "1"
    }
    # Custom event bus to handle events between threads, can add locks, or other features as needed
    # Make all methods static so that we don't need to instantiate the class

    @staticmethod
    def publish(event):
        EventBus.put(event)
    
    def put(event):
        opcode = EventBus.extract_opcode(event).decode('utf-8')
        EventBus._queues[opcode].put(event)

    @staticmethod
    def message_builder(opcode, payload):
        encoding_type = opcode[codes.POSITION_OF_ENCODING_TYPE]

        match encoding_type:
            case "0":
                encoded_payload = payload.encode('utf-8')
            case "1":
                encoded_payload = pickle.dumps(payload)
            case "2":
                encoded_payload = EventBus.encoded_format_json(payload, opcode[codes.POSITION_OF_SUBJECT])
            case _:
                raise ValueError(f"Unknown encoding type: {encoding_type}")

        return opcode.encode('utf-8') + encoded_payload

    @staticmethod
    def encoded_format_json(payload, format_spec):
        match format_spec:
            case correct_type if correct_type in codes.ENCODING_TYPE_ADDRESS_JSON:
                packet = json.dumps({ 
                    "address": {
                        "ip": payload[0],
                        "port": payload[1]
                    }
                })
                return packet.encode('utf-8')
            case "7":
                packet = json.dumps({
                    "consent_form": {
                        "target_name": payload[0],
                        "response": payload[1]
                    }
                })
                return packet
            case _:
                raise ValueError("Unsupported format specifier for JSON encoding")
    
    def encoded_format_list(payload, format_spec):
        match format_spec:
            case "2": 
                return pickle.dumps(payload)

    @staticmethod
    def get(block=False,timeout=None):
        try:
            event = EventBus._queue.get(block=block,timeout=timeout)   
            return EventBus.__parse_event(event)
        except Exception as e:
            raise e
    
    @staticmethod
    def extract_opcode(event):
        return event[:codes.opcode_length]
    
    @staticmethod
    def extract_payload(event):
        return event[codes.opcode_length:]
    
    @staticmethod
    def isEmpty():
        return EventBus._queue.empty()
    
    @staticmethod
    def decompose_event(event):
        return (EventBus.extract_opcode(event), EventBus.extract_payload(event))

    def decode_payload(opcode, payload):
        match opcode[codes.POSITION_OF_ENCODING_TYPE]:  # Check the second digit of the opcode
            case "0": # UTF-8 encoded payload
                return payload.decode('utf-8')
            case "1": # Pickle encoded payload
                list = pickle.loads(payload)
                return {
                    "formatted": EventBus.format_payload_list(opcode, list),
                    "values": list
                }
            case "2": # JSON encoded payload
                return EventBus.format_payload_json(json.loads(payload),opcode[codes.POSITION_OF_SUBJECT])


    def format_payload_json(payload, format_spec):
        match format_spec:
            case correct_type if correct_type in codes.ENCODING_TYPE_ADDRESS_JSON:
                address = payload['address']
                return (address['ip'],address['port'])


    def format_payload_list(opcode, payload):
        def numbered(values):
            return "\n".join(f"{i}. {value}"for i, value in enumerate(values, start=1)) + "\n"
        match opcode[codes.POSITION_OF_SUBJECT]:
            case "2":
                return numbered(payload.values())
            case "6":
                return "Available encryption methods:\n" + numbered(payload.values())

    @staticmethod
    def parse_event(event, return_opcode = False):
        opcode = EventBus.extract_opcode(event).decode('utf-8') # all opcodes are utf-8 encoded
        payload = EventBus.extract_payload(event) # to decode in parser
        if return_opcode:
            return opcode,EventBus.decode_payload(opcode,payload)
        return (EventBus.decode_payload(opcode, payload))
    

    def get_from_queue(opcode, block=True, timeout=0.5):
        event = EventBus._queues[opcode].get(block=block, timeout=timeout)
        return EventBus.parse_event(event)