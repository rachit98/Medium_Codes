import time
from flask import Flask, request, jsonify

app = Flask(__name__)

CAPACITY = 10
STATUS = "UP"
REQUESTS_IN_QUEUE = 0
PORT = 5001
NAME = "SERVER 1"

@app.route('/')
def api():
    return "SERVER 1"

@app.route('/queue')
def queue():
    return str(REQUESTS_IN_QUEUE)

@app.route('/down')
def down():
    global STATUS
    STATUS = "DOWN"
    return STATUS


@app.route('/up')
def up():
    global STATUS
    STATUS = "UP"
    return STATUS


@app.route('/state')
def state():
    return jsonify({'NAME': NAME, 'CAPACITY': CAPACITY, 'REQUESTS IN QUEUE': REQUESTS_IN_QUEUE, 'STATUS': STATUS, 'PORT': PORT})

@app.route('/turnoff')
def turnoff():
    global REQUESTS_IN_QUEUE
    REQUESTS_IN_QUEUE = 0
    return jsonify({'NAME': NAME, 'CAPACITY': CAPACITY, 'REQUESTS IN QUEUE': REQUESTS_IN_QUEUE, 'STATUS': STATUS, 'PORT': PORT})

@app.route('/process_request')
def process_request():
    global REQUESTS_IN_QUEUE
    if REQUESTS_IN_QUEUE == 0:
        return "No requests in queue to process"
    else:
        REQUESTS_IN_QUEUE -= 1
        return state()


@app.route('/add_request')
def add_request():
    global REQUESTS_IN_QUEUE, CAPACITY
    if REQUESTS_IN_QUEUE == CAPACITY:
        return "Server full, can't add request"
    else:
        REQUESTS_IN_QUEUE += 1
        return state()


if __name__ == '__main__':
    app.run(port=PORT)
