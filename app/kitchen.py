from flask import Flask, request
from components.orders import *
from components.foods import menu
from cooks.cook import *
from threading import Thread

# Create a Flask object called app
app = Flask(__name__)

# Array to store the threads
threads = []

@app.route('/order', methods = ['GET', 'POST'])

def order():
    data = request.get_json()
    add_order(data)
    print(f'A new order is received from the waiter. Order nr.{data["order_id"]}\n')
    return {'success': True}

def add_order(order):
    received_order = {
        'table_id': order['table_id'],
        'order_id': order['order_id'],
        'items': order['items'],
        'items_number': len(order['items']),
        'priority': order['priority'],
    }
    order_queue.put(received_order)
    for id in received_order['items']:
        order_item = next((item for i, item in enumerate(menu) if item['id'] == id), None)
        if order_item is not None:
            ordered_food_queue.put({'order_id': order['order_id'], 'food_id': order_item['id']})
    
def run_kitchen():
    kitchen_thread = Thread(target=lambda: app.run(host = '0.0.0.0', port = 8000, debug = False, use_reloader = False), daemon = True)
    kitchen_thread.start()
    # Create thread Client
    cook_thread = Cook()
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