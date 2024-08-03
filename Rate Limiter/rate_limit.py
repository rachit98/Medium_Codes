import time
from flask import Flask, request, jsonify
from collections import deque
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Rate Limited API"
    }
)

app.register_blueprint(swaggerui_blueprint)

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

@app.route('/api')
@rate_limited
def api():
    return jsonify({'message': "Ping successful"})

@app.route('/static/swagger.json')
def swagger_json():
    return jsonify({
        "swagger": "2.0",
        "info": {
             "title": "Rate Limited API",
            "version": "1.0",
            },
        "paths": {
            "/api": {
                "get": {
                    "summary": "Test rate limit",
                    "responses": {
                        200: {
                            "description": "Success"
                        },
                        429: {
                            "description": "Failure"
                        },
                    },
                }
            }
        }

    })

if __name__ == '__main__':
    app.run()
