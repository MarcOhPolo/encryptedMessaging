from queue import Queue
from server import codes
import pickle
import json

class EventBus:
    _queue = Queue()

    # Custom event bus to handle events between threads, can add locks, or other features as needed
    # Make all methods static so that we don't need to instantiate the class


    #TODO: MAKE ERROR HANDLING


    @staticmethod
    def publish(event):
        EventBus._queue.put(event)

    @staticmethod
    def get(block=False,timeout=None):
        event = EventBus._queue.get(block=block,timeout=timeout)
        return EventBus._parse_event(event)
    
    @staticmethod
    def _extract_opcode(event):
        return event[:codes.opcode_length]
    
    @staticmethod
    def _extract_payload(event):
        return event[codes.opcode_length:]
    
    @staticmethod
    def isEmpty():
        return EventBus._queue.empty()
    
    @staticmethod
    def _decompose_event(event):
        return (EventBus._extract_opcode(event), EventBus._extract_payload(event))

    def _decode_payload(opcode, payload):
        match opcode[codes.opcode_length-2]:  # Check the second digit of the opcode
            case "0":
                return payload.decode('utf-8')
            case "1":
                list = pickle.loads(payload)
                return EventBus._format_payload_list(opcode, list)
            case "2":
                json.loads(payload)
    
    def _format_payload_list(opcode, payload):
        match opcode[codes.opcode_length-1]:  # Check the last digit of the opcode
            case "2":  # User list
                i=1
                list = ""
                for str in payload.values():
                    list += f"{i}. {str}\n"
                    i+=1
                return list
            case "6":  # Encryption methods
                i=1
                list = "Available encryption methods:\n"
                for str in payload.values():
                    list += f"{i}. {str}\n"
                    i+=1
                return list


    def _parse_event(event):
        opcode = EventBus._extract_opcode(event).decode('utf-8') # all opcodes are utf-8 encoded
        payload = EventBus._extract_payload(event) # to decode in parser
        return (EventBus._decode_payload(opcode, payload))