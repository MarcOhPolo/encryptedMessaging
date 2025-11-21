from queue import Queue
from collections import deque
from server import codes
import pickle

class EventBus:
    _queue = Queue()

    # Custom event bus to handle events between threads, can add locks, or other features as needed
    # Make all methods static so that we don't need to instantiate the class


    #TODO: MAKE ERROR HANDLING


    @staticmethod
    def publish(event):
        EventBus._queue.put(event)

    @staticmethod
    def get():
        event = EventBus._queue.get(True)
        return EventBus._parse_event(event)
    
    @staticmethod
    def _extract_opcode(event):
        return event[:codes.opcode_length]
    
    @staticmethod
    def _extract_payload(event):
        return event[codes.opcode_length:]
    
    @staticmethod
    def _decompose_event(event):
        return (EventBus._extract_opcode(event), EventBus._extract_payload(event))

    def _decode_payload(opcode, payload):
        match opcode[codes.opcode_length-2]:  # Check the second digit of the opcode
            case "0":
                return payload.decode('utf-8')
            case "1":
                i=1
                parsed = ""
                for str in pickle.loads(payload).values():
                    parsed = parsed + (f"{i}: {str}\n")
                    i+=1
                return parsed
    
    def _parse_event(event):
        opcode = EventBus._extract_opcode(event).decode('utf-8') # all opcodes are utf-8 encoded
        payload = EventBus._extract_payload(event) # to decode in parser
        return (EventBus._decode_payload(opcode, payload))