import time
import requests
from flask import Flask, request, jsonify
from collections import deque
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
PORT = 5000

REQUESTS_IN_QUEUE = 0

call_history = {}
max_calls = 5
time_frame = 60

def rate_limited(func):
    def wrapper(*args, **kwargs):
        ip_address = request.remote_addr
        if ip_address not in call_history:
            call_history[ip_address] = deque()

        queue = call_history[ip_address]
        current_time = time.time()

        while queue and current_time - queue[0] > time_frame:
            queue.popleft()

        if len(queue) >= max_calls:
            return jsonify({"error": "Rate limit exceeded, try after some time"})

        queue.append(current_time)
        return func(*args, **kwargs)

    return wrapper
@scheduler.task('interval', id='run_every_10_second', seconds=10)
@app.route('/')
def scheduled_task():
    global REQUESTS_IN_QUEUE
    url = "http://127.0.0.1:"
    resp1 = requests.get(url + '5001' + '/state')
    resp2 = requests.get(url + '5002' + '/state')
    resp3 = requests.get(url + '5003' + '/state')
    print({'Server1': resp1.json(), 'Server2': resp2.json(), 'Server3': resp3.json()})
    if resp1.json()['STATUS'] != 'UP':
        REQUESTS_IN_QUEUE = REQUESTS_IN_QUEUE + int(resp1.json()['REQUESTS IN QUEUE'])
        requests.get(url + '5001' + '/turnoff')
        print('SERVER 1 is DOWN')

    if resp2.json()['STATUS'] != 'UP':
        REQUESTS_IN_QUEUE = REQUESTS_IN_QUEUE + int(resp2.json()['REQUESTS IN QUEUE'])
        requests.get(url + '5002' + '/turnoff')
        print('SERVER 2 is DOWN')

    if resp3.json()['STATUS'] != 'UP':
        REQUESTS_IN_QUEUE = REQUESTS_IN_QUEUE + int(resp3.json()['REQUESTS IN QUEUE'])
        requests.get(url + '5003' + '/turnoff')
        print('SERVER 3 is DOWN')
    print({'LB': REQUESTS_IN_QUEUE, 'Server1': resp1.json(), 'Server2': resp2.json(), 'Server3': resp3.json()})
    return {'Server1': resp1.json(), 'Server2': resp2.json(), 'Server3': resp3.json()}


@app.route('/status')
def check_status():
    global REQUESTS_IN_QUEUE
    status_obj = {}
    status_obj['REQUESTS_IN_QUEUE'] = str(REQUESTS_IN_QUEUE)
    url = "http://127.0.0.1:"
    resp1 = requests.get(url + '5001' + '/queue')
    resp2 = requests.get(url + '5002' + '/queue')
    resp3 = requests.get(url + '5003' + '/queue')
    status_obj['SERVER1'] = str(resp1.text)
    status_obj['SERVER2'] = str(resp2.text)
    status_obj['SERVER3'] = str(resp3.text)
    return status_obj


@app.route('/process_queue')
@scheduler.task('interval', id='run_every_second', seconds=1)
def process_queue():
    global REQUESTS_IN_QUEUE
    if REQUESTS_IN_QUEUE == 0:
        return {}
    url = "http://127.0.0.1:"
    resp1 = requests.get(url + '5001' + '/state')
    resp2 = requests.get(url + '5002' + '/state')
    resp3 = requests.get(url + '5003' + '/state')

    if resp1.json()['STATUS'] != 'UP':
        space1 = 0
    else:
        space1 = 10 - int(requests.get(url + '5001' + '/queue').text)

    if resp2.json()['STATUS'] != 'UP':
        space2 = 0
    else:
        space2 = 10 - int(requests.get(url + '5002' + '/queue').text)

    if resp3.json()['STATUS'] != 'UP':
        space3 = 0
    else:
        space3 = 10 - int(requests.get(url + '5003' + '/queue').text)
    space = [space1, space2, space3]
    if space1 == max(space) and space1 > 0:
        requests.get(url + '5001' + '/add_request')
        REQUESTS_IN_QUEUE -= 1
        return "Request added to Server 1"
    elif space2 == max(space) and space2 > 0:
        requests.get(url + '5002' + '/add_request')
        REQUESTS_IN_QUEUE -= 1
        return "Request added to Server 2"
    elif space3 == max(space) and space3 > 0:
        requests.get(url + '5003' + '/add_request')
        REQUESTS_IN_QUEUE -= 1
        return "Request added to Server 3"
    else:
        return "Cant process now"


@app.route('/new_request')
@rate_limited
def add_request():
    global REQUESTS_IN_QUEUE
    url = "http://127.0.0.1:"
    resp1 = requests.get(url + '5001' + '/state')
    resp2 = requests.get(url + '5002' + '/state')
    resp3 = requests.get(url + '5003' + '/state')

    if resp1.json()['STATUS'] != 'UP':
        space1 = 0
    else:
        space1 = 10 - int(requests.get(url + '5001' + '/queue').text)

    if resp2.json()['STATUS'] != 'UP':
        space2 = 0
    else:
        space2 = 10 - int(requests.get(url + '5002' + '/queue').text)

    if resp3.json()['STATUS'] != 'UP':
        space3 = 0
    else:
        space3 = 10 - int(requests.get(url + '5003' + '/queue').text)

    space = [space1, space2, space3]
    if space1 == max(space) and space1 > 0:
        requests.get(url + '5001' + '/add_request')
        return "Request added to Server 1"
    elif space2 == max(space) and space2 > 0:
        requests.get(url + '5002' + '/add_request')
        return "Request added to Server 2"
    elif space3 == max(space) and space3 > 0:
        requests.get(url + '5003' + '/add_request')
        return "Request added to Server 3"
    else:
        REQUESTS_IN_QUEUE += 1
        return "Request added to Queue, will add to server once requests are processed"


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(port=PORT)
