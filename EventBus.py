from queue import Queue
class EventBus:
    _queue = Queue()

    #Custom event bus to handle events between threads, can add locks, or other features as needed

    @staticmethod
    def publish(event):
        EventBus._queue.put(event)

    @staticmethod
    def get(opcode=None):
        # TODO: use parameter to specify what kind of event is being requested so that the bus filters appropriately
        return EventBus._queue.get()