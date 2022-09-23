from threading import Thread
from components.orders import *
import requests
import time
from components.foods import menu
import threading

time_unit = 1

# Customized Cook class extending the Thread class
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
            self.cook_proficiency()    
          
    def cook_proficiency(self):
        for i in range(self.proficiency):
            cooking_thread = Thread(target = self.cook_order, name = f'{self.name} - Task {i}\n')
            cooking_thread.start() 
            cooking_thread.join()
                              
    # Method to cook an order
    def cook_order(self):
        try:
            # Get a food item from the queue
            food = ordered_food_queue.get()
            # Get the food information from the menu
            food_info = None
            for info in menu:
                if info['id'] == food['id']:
                    food_info = info
            # Get information of food's order
            food_order_id = None
            food_order_info = None
            for id, order in enumerate(order_queue):
                if order['order_id'] == food['order_id']:
                    food_order_id = id
                    food_order_info = order
            # Number of foods in the order
            number_of_foods = food_order_info['items_number']
            # Check if the cook can prepare the food
            if food_info['complexity'] == self.rank or food_info['complexity'] == self.rank - 1:
                # Preparation time
                time.sleep(food_info['preparation-time'] * time_unit)
                # Message that the cook is cooking the food
                print(f'Cook {threading.current_thread().name} is cooking {food_info["name"]} (nr.{food_info["id"]}) for order nr.{food_order_info["order_id"]}\n')
                # Count the prepared foods in the order
                order_queue[food_order_id]['cooked_foods'] += 1
                # Check if all the foods are ready
                if order_queue[food_order_id]['cooked_foods'] == number_of_foods:
                    # Set the time when the order is ready
                    finished_cooking_time = time.time()
                    # Add the cooking details to the order
                    order_queue[food_order_id]['cooking_details'].append({'food_id': food_info['id'], 'cook_id': self.id})
                    food = ordered_food_queue.task_done()
                    # Message that the order is ready
                    print(f'Order nr.{order["order_id"]} is ready. It took {finished_cooking_time} time units to prepare it. From {self.name}: {self.catch_phrase}\n')
                    # Put the order data in a dictionary
                    payload = dict({
                        'order_id': order_queue[food_order_id]['order_id'], 
                        'table_id': order_queue[food_order_id]['table_id'], 
                        'waiter_id': order['waiter_id'],
                        'items': order['items'], 
                        'priority': order['priority'],
                        'wait_time': order['wait_time'],
                        'pick_up_time': order['pick_up_time'],
                        'cooking_time': int(finished_cooking_time) - int(order_queue[food_order_id]['receive_time']),
                        'cooking_details': order_queue[food_order_id]['cooking_details']
                    })
                    requests.post('http://localhost:3000/distribution', json = payload, timeout = 0.0001)
                    # requests.post('http://dininghall:3000/distribution', json = payload, timeout = 0.0001)
            # If the cook cannot prepare the food, put it back in the queue
            else:
                ordered_food_queue.put(food)
        # Exceptions
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            pass 