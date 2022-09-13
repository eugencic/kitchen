from flask import Flask, request

app = Flask(__name__)

@app.route('/order', methods = ['GET', 'POST'])

def order():
    data = request.get_json()
    print(data["order_id"])

def run_kitchen():
    app.run(host = '0.0.0.0', port = 8000, debug = False)

if __name__ == '__main__':
    run_kitchen()