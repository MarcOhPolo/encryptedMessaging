from queue import Queue
from codes import *
import registry


class EventBus:

    # Initialize queues for each opcode that requires event handling from the client
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
                encoder = registry.ENCODERS[opcode]
            except KeyError:
                raise ValueError(f"No encoder registered for opcode {opcode}")
            return opcode.encode('utf-8') + encoder(payload)
    
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
            try:
                decoder = registry.DECODERS[opcode]
            except KeyError:
                raise ValueError(f"No decoder registered for opcode {opcode}")
            return decoder(payload)

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