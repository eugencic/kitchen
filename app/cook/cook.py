from threading import Thread
from components.orders import *
import requests
import time
from components.foods import menu
import threading
from components.apparatuses import *

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
            # Execute the function to cook foods
            self.cook_proficiency()   
    
    # Cook foods according to proficiency
    def cook_proficiency(self):
        for i in range(self.proficiency):
            # Create a thread to cook a food
            cooking_thread = Thread(target = self.cook_food, name = f'Cook {self.name} - Task {i}')
            cooking_thread.start() 
            cooking_thread.join()
                              
    # Method to cook an order
    def cook_food(self):
        try:
            # Get a food item from the queue
            food = ordered_food_queue.get().ready_item
            # Priority of the item
            priority = -(int(food['priority']))
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
                # Check the required cooking apparatus for the food
                cooking_apparatus = food_info['cooking-apparatus']
                if cooking_apparatus == 'stove':
                    # Wait till there is an available stove
                    while stoves_queue.empty() == True:
                        time.sleep(1)
                    # Check if there are any available stoves
                    if stoves_queue.empty() == False:
                        # Use the stove
                        stoves_queue.get()
                        # Output message
                        print(f'{threading.current_thread().name} is cooking {food_info["name"]} (nr.{food_info["id"]}) for order nr.{food_order_info["order_id"]} using stove\n')
                        # Stove thread
                        stove_thread = Thread(target = cookInStove, args = (stoves_queue, food_info['preparation-time'],))
                        # Start the thread
                        stove_thread.start()
                        # Wait if the thread is still running
                        while stove_thread.is_alive():
                            time.sleep(1)
                        # Wait until the thread ends
                        stove_thread.join()
                        if stoves_queue.full() == False:
                            print(f'The food in the stove is cooked\n')
                            print(f'The {food_info["name"]} (nr.{food_info["id"]}) is ready. A stove is free\n')
                            # Release a stove
                            stoves_queue.task_done()
                            # Add it back in the queue
                        stoves_queue.put(0)
                elif cooking_apparatus == 'oven':
                    # Wait till the is an available stove
                    while ovens_queue.empty() == True:
                        time.sleep(1)
                    # Check if the oven is available
                    if ovens_queue.empty() == False:
                        # Use the oven
                        ovens_queue.get()
                        # Output message
                        print(f'{threading.current_thread().name} is cooking {food_info["name"]} (nr.{food_info["id"]}) for order nr.{food_order_info["order_id"]} using oven\n')
                        # Oven thread
                        oven_thread = Thread(target = cookInOven, args = (ovens_queue, food_info['preparation-time'],))
                        # Start the thread
                        oven_thread.start()
                        # Wait if the thread is still running
                        while oven_thread.is_alive():
                            time.sleep(1)
                        # Wait until the thread ends
                        oven_thread.join()
                        print(f'Oven cooking has finished\n')
                        if ovens_queue.qsize() == 0:
                            print(f'The {food_info["name"]} (nr.{food_info["id"]}) is ready. The oven in free\n')
                            # Release the oven
                            ovens_queue.task_done()
                            # Add it back in the queue
                            ovens_queue.put(0)
                # If there is no need for cooking apparatus
                elif cooking_apparatus is None:
                    print(f'{threading.current_thread().name} is cooking {food_info["name"]} (nr.{food_info["id"]}) for order nr.{food_order_info["order_id"]}\n')
                    # Preparation time
                    time.sleep(food_info['preparation-time'] * time_unit)
                # Count the prepared foods in the order
                order_queue[food_order_id]['cooked_foods'] += 1
                # Check if all the foods are ready
                if order_queue[food_order_id]['cooked_foods'] == number_of_foods:
                    # Set the time when the order is ready
                    finished_cooking_time = time.time()
                    # Add the cooking details to the order
                    order_queue[food_order_id]['cooking_details'].append({'food_id': food_info['id'], 'cook_id': self.id})
                    # Order task is complete
                    food = ordered_food_queue.task_done()
                    # Message that the order is ready
                    print(f'Order nr.{order["order_id"]} is ready. From {self.name}: {self.catch_phrase}\n')
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
                    # Send the order to the dining hall
                    #requests.post('http://localhost:3000/distribution', json = payload, timeout = 0.0001)
                    requests.post('http://dininghall:3000/distribution', json = payload, timeout = 0.0001) 
            # If the cook cannot prepare the food, put it back in the queue
            else:
                ordered_food_queue.put(Prioritize(priority, food))
        # Exceptions
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            pass 