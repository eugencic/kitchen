from threading import Thread
from components.orders import *
import requests
import time
from components.foods import menu
import threading

time_unit = 1

# Customized Waiter class extending the Thread class
class Cook(Thread):
    def __init__(self, data, *args, **kwargs):
        # Access methods of the base class
        super(Cook, self).__init__(*args, **kwargs)
        self.daemon = True
        self.id = data['id']
        self.rank = data['rank']
        self.proficiency = data['proficiency']
        self.name = data['name']
        self.catch_phrase = data['catch-phrase']

    # Represent the thread's activity
    def run(self):
        while True:
            # Execute the function to cook an order
            self.cook_order()
            
    # Method to cook an order
    def cook_order(self):
        try:
            # Get a food item from the queue
            food = ordered_food_queue.get()
            # Get the food information from the menu
            food_info = next((info for info in menu if info['id'] == food['id']), None)
            # Get the order information of the order where the food is stored
            food_order_id = None
            food_order_info = None
            for id, order in enumerate(order_queue):
                if order['order_id'] == food['order_id']:
                    food_order_id = id
                    food_order_info = order
            number_of_foods = food_order_info['items_number']
            # Check if the cook can prepare the food
            if food_info['complexity'] == self.rank or food_info['complexity'] == self.rank - 1:
                print(f'{threading.current_thread().name} is cooking the {food_info["name"]}(nr.{food_info["id"]}) for order nr.{food_order_info["order_id"]}')
                time.sleep(food_info['preparation-time'] * time_unit)
                order_queue[food_order_id]['cooked_foods'] += 1
                if order_queue[food_order_id]['cooked_foods'] == number_of_foods:
                    finished_cooking_time = int(time.time())
                    print(f'The cook finished cooking the food nr.{food_info["id"]} from the order nr.{order["order_id"]}. It took {finished_cooking_time} time units to prepare it. {self.catch_phrase}\n')
                    order_queue[food_order_id]['cooking_details'].append({'food_id': food_info['id'], 'cook_id': self.id})
                    food = ordered_food_queue.task_done()
                    payload = dict({
                        'order_id': order_queue[food_order_id]['order_id'], 
                        'table_id': order_queue[food_order_id]['table_id'], 
                        'waiter_id': order['waiter_id'],
                        'items': order['items'], 
                        'priority': order['priority'],
                        'wait_time': order['wait_time'],
                        'pick_up_time': order['pick_up_time'],
                        'cooking_time': finished_cooking_time - int(order_queue[food_order_id]['receive_time']),
                        'cooking_details': order_queue[food_order_id]['cooking_details']
                    })
                    # requests.post('http://dininghall:3000/distribution', json = payload, timeout = 0.0001)
                    requests.post('http://localhost:3000/distribution', json = payload, timeout = 0.0001)
            else:
                ordered_food_queue.put(food)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            pass