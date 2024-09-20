class EventBus:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventBus, cls).__new__(cls, *args, **kwargs)
            cls._instance.listeners = {}
        return cls._instance

    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)
            if not self.listeners[event_type]:
                del self.listeners[event_type]

    def publish(self, event_type, **kwargs):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                if kwargs:
                    callback(**kwargs)
                else:
                    callback()


# Global instance of the event bus
event_bus = EventBus()
