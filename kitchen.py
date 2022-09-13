from flask import Flask, request
from components.orders import *

app = Flask(__name__)

@app.route('/order', methods = ['GET', 'POST'])

def order():
    data = request.get_json()
    add_order(data)
    print(f' A new order is received from the waiter. Order nr.{data["order_id"]}')
    return {'success': True}

def add_order(order):
    received_order = {
        'table_id': order['table_id'],
        'order_id': order['order_id'],
        'items': order['items'],
        'priority': order['priority'],
    }
    order_queue.put(received_order)
    
def run_kitchen():
    app.run(host = '0.0.0.0', port = 8000, debug = False)

if __name__ == '__main__':
    run_kitchen()