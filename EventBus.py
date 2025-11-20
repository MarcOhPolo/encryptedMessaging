from queue import Queue
from server import codes

class EventBus:
    _queue = Queue()

    #Custom event bus to handle events between threads, can add locks, or other features as needed

    @staticmethod
    def publish(event):
        EventBus._queue.put(event)

    @staticmethod
    def get(opcode=None):
        # TODO: use parameter to specify what kind of event is being requested so that the bus filters appropriately
        if opcode:
            for event in list(EventBus._queue.queue):
                if EventBus.__startswithopcode(event, opcode)==opcode:
                    return event
        return EventBus._queue.get()
    
    @staticmethod
    def __startswithopcode(event):
        return event[:len(codes.opcode_length)]