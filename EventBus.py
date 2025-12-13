from queue import Queue
from server import codes
import pickle
import json

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
        opcode = EventBus.__extract_opcode(event).decode('utf-8')
        EventBus._queues[opcode].put(event)

    @staticmethod
    def get(block=False,timeout=None):
        event = EventBus._queue.get(block=block,timeout=timeout)
        return EventBus.__parse_event(event)
    
    @staticmethod
    def __extract_opcode(event):
        return event[:codes.opcode_length]
    
    @staticmethod
    def __extract_payload(event):
        return event[codes.opcode_length:]
    
    @staticmethod
    def isEmpty():
        return EventBus._queue.empty()
    
    @staticmethod
    def __decompose_event(event):
        return (EventBus.__extract_opcode(event), EventBus.__extract_payload(event))

    def __decode_payload(opcode, payload):
        match opcode[codes.POSITION_OF_ENCODING_TYPE]:  # Check the second digit of the opcode
            case "0":
                return payload.decode('utf-8')
            case "1":
                list = pickle.loads(payload)
                return EventBus.__format_payload_list(opcode, list)
            case "2":
                return json.loads(payload)
    
    def __format_payload_list(opcode, payload):
        def numbered(values):
            return "\n".join(f"{i}. {value}"for i, value in enumerate(values, start=1)) + "\n"
        match opcode[codes.POSITION_OF_SUBJECT]:
            case "2":
                return numbered(payload.values())
            case "6":
                return "Available encryption methods:\n" + numbered(payload.values())


    def __parse_event(event):
        opcode = EventBus.__extract_opcode(event).decode('utf-8') # all opcodes are utf-8 encoded
        payload = EventBus.__extract_payload(event) # to decode in parser
        return (EventBus.__decode_payload(opcode, payload))
    
    def get_from_queue(opcode, block=True, timeout=0.5):
        event = EventBus._queues[opcode].get(block=block, timeout=timeout)
        return EventBus.__parse_event(event)