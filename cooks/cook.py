from threading import Thread
from components.orders import *
import requests

# Customized Waiter class extending the Thread class
class Cook(Thread):
    def __init__(self, *args, **kwargs):
        # Access methods of the base class
        super(Cook, self).__init__(*args, **kwargs)

    # Represent the thread's activity
    def run(self):
        while True:
            # Execute the function to cook an order
            self.cook_order()
            
    # Method to cook an order
    def cook_order(self):
        try:
            order = order_queue.get()
            number_of_foods = order['items_number']
            for f in range(0, number_of_foods):
                food = ordered_food_queue.get()
                print(f'The cook finished cooking the food nr.{food["food_id"]} from the order nr.{food["order_id"]}.')
                ordered_food_queue.task_done()
            order_queue.task_done()
            # Put the order data in a dictionary
            payload = dict({'table_id': order['table_id'], 'order_id': order['id'], 'items': order['items'], 'priority': order['priority']})
            requests.post('http://localhost:3000/distribution', json = payload, timeout = 0.0001)
        except (Exception, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            pass