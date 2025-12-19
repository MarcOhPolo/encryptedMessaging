from queue import Queue
from codes import *
import pickle
import json
from registry import ENCODERS


class EventBus:

    # Initialize queues for each opcode that requires event handling for the client
    _queues = {opcode: Queue() for opcode in server_to_client_group}

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
            try:
                encoder = ENCODERS[opcode]
            except KeyError:
                raise ValueError(f"No encoder registered for opcode {opcode}")
            return opcode.encode('utf-8') + encoder(payload)
    
    def encode_simple_utf(payload):
        return payload.encode('utf-8')
    
    def encode_pickle(payload):
        return pickle.dumps(payload)
    
    def encode_format_json_ipv4_address(payload):
        packet = json.dumps({ 
                        "address": {
                            "ip": payload[0],
                            "port": payload[1]
                        }
                    }
                )
        return packet.encode('utf-8')
    
    def encode_format_json_p2p_request(payload):
        packet = json.dumps({
                    "consent_form": {
                        "target_name": payload[0],
                        "response": payload[1]
                    }
                }
            )
        return packet.encode('utf-8')

    @staticmethod
    def get(block=False,timeout=None):
        try:
            event = EventBus._queue.get(block=block,timeout=timeout)   
            return EventBus.__parse_event(event)
        except Exception as e:
            raise e
    
    @staticmethod
    def extract_opcode(event):
        return event[:opcode_length]
    
    @staticmethod
    def extract_payload(event):
        return event[opcode_length:]
    
    @staticmethod
    def isEmpty():
        return EventBus._queue.empty()
    
    @staticmethod
    def decompose_event(event):
        return (EventBus.extract_opcode(event), EventBus.extract_payload(event))

    def decode_payload(opcode, payload):
        match opcode[POSITION_OF_ENCODING_TYPE]:  # Check the second digit of the opcode
            case "0": # UTF-8 encoded payload
                return payload.decode('utf-8')
            case "1": # Pickle encoded payload
                list = pickle.loads(payload)
                return {
                    "formatted": EventBus.format_payload_list(opcode, list),
                    "values": list
                }
            case "2": # JSON encoded payload
                return EventBus.format_payload_json(json.loads(payload),opcode[POSITION_OF_SUBJECT])


    def format_payload_json(payload, format_spec):
        match format_spec:
            case correct_type if correct_type in ENCODING_TYPE_ADDRESS_JSON:
                address = payload['address']
                return (address['ip'],address['port'])


    def format_payload_list(opcode, payload):
        def numbered(values):
            return "\n".join(f"{i}. {value}"for i, value in enumerate(values, start=1)) + "\n"
        match opcode[POSITION_OF_SUBJECT]:
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