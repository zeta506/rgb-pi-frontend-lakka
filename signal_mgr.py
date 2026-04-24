import queue
import threading
import time
import rtk

class Singleton(type):
    __instance = None
    __instances = {}

def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
        cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

class Signal_Manager(metaclass=Singleton):
    sig_map = {}
    asynq = queue.Queue()

    def __init__(self):
        t = threading.Thread(target=self.__listen)
        t.daemon = True
        t.start()

    def __listen(self):
        while True:
            if self.asynq.empty():
                time.sleep(2) # Time lapse for async queued signal check
            else:
                signal, args, kwargs = self.asynq.get()
                self.emit(signal, *args, **kwargs)

    def connect(self, signal, slot):
        ''' Connect signal with slot to receive message '''
        if signal not in self.sig_map.keys():
            self.sig_map[signal] = []
        self.sig_map[signal].append(slot)

    def disconnect(self, signal, slot):
        ''' Disconnect signal message '''
        if signal in self.sig_map.keys():
            if slot in self.sig_map[signal]:
                self.sig_map[signal].remove(slot)

    def emit(self, signal, *args, **kwargs):
        ''' Synchronous emission '''
        if signal in self.sig_map.keys():
            for s in self.sig_map[signal]:
                if rtk.logger_root_level in ('DEBUG','INFO'):
                    s(*args, **kwargs)
                else:
                    try:
                        s(*args, **kwargs)
                    except Exception as error:
                        rtk.logging.error('Signal %s error: %s', signal, error)

    def amit(self, signal, *args, **kwargs):
        ''' Asyncrhonous emission. Immediately return. No context hang '''
        self.asynq.put([signal, args, kwargs])

    def nmit(self, signal, *args, **kwargs):
        ''' N thread asynchronus emission. Immediately return. No context hang '''
        t = threading.Thread(target=lambda: self.emit(signal, *args, **kwargs))
        t.daemon = True
        t.start()