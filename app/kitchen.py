from flask import Flask, request
from components.orders import *
from components.foods import menu
from cooks.cook import *
from threading import Thread
from components.cooks import cooks

# Create a Flask object called app
app = Flask(__name__)

# Array to store the threads
threads = []

# App route
@app.route('/order', methods = ['GET', 'POST'])

def order():
    data = request.get_json()
    add_order(data)
    print(f'A new order is received from the waiter. Order nr.{data["order_id"]}.\n')
    return {'success': True}

def add_order(order):
    # Put the received data in a dict
    received_order = {
        'order_id': order['order_id'],
        'table_id': order['table_id'],
        'waiter_id': order['waiter_id'],
        'items': order['items'],
        'items_number': len(order['items']),
        'priority': order['priority'],
        'wait_time': order['max_wait'],
        'pick_up_time': order['pick_up_time'],
        'receive_time': time.time(),
        'cooking_details': [],
        'cooked_foods': 0
    }
    # Put the food from order for preparing
    for item_id in received_order['items']:
        order_item = None
        for i, item in enumerate(menu):
            if item['id'] == item_id:
                order_item = item
        if order_item is not None:
            ordered_food_queue.put({'id': order_item['id'], 'order_id': order['order_id']})
    # Put the order in a queue
    order_queue.append(received_order)
    # Sort the orders by priority
    def get_priority(item):
        return item['priority']
    order_queue = order_queue(key = get_priority)
    
def run_kitchen():
    kitchen_thread = Thread(target=lambda: app.run(host = '0.0.0.0', port = 8000, debug = False, use_reloader = False), daemon = True)
    kitchen_thread.start()
    for _, cook in enumerate(cooks):
        # Create thread Client
        cook_thread = Cook(cook)
        # Add the thread to the array
        threads.append(cook_thread)
    # Start the threads
    for thread in threads:
        thread.start()
    # Wait for the threads to complete    
    for thread in threads:
        thread.join()
        

if __name__ == '__main__':
    run_kitchen()