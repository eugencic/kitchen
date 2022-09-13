from flask import Flask

app = Flask(__name__)

@app.route('/order')

def run_kitchen():
    app.run(host = '0.0.0.0', port = 8000, debug = True)

if __name__ == '__main__':
    run_kitchen()