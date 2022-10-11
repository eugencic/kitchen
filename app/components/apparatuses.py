import queue
import time

global stoves_queue
global ovens_queue

stoves_queue = queue.Queue(maxsize=2)
ovens_queue = queue.Queue(maxsize=1)
stoves_queue.put(0)
stoves_queue.put(1)
ovens_queue.put(0)

# Function for stove thread
def cookInStove(q, preparation_time):
        time.sleep(preparation_time)

# Function for oven thread      
def cookInOven(q, preparation_time):
        time.sleep(preparation_time)