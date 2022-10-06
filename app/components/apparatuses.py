import queue

global stoves_queue
global ovens_queue

stoves_queue = queue.Queue(maxsize = 2)
ovens_queue = queue.Queue(maxsize = 1)
stoves_queue.put(0)
stoves_queue.put(1)
ovens_queue.put(0)