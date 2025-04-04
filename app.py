from flask import Flask, jsonify, request
import requests
import os
from time import time
import queue
import threading
from urllib.parse import urlencode
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)

def make_request(url, params, result_queue):
    try:
        if params:
            url_with_params = f"{url}?{urlencode(params)}"
        else:
            url_with_params = url

        logging.info(f"Making request to URL: {url_with_params}")
        start = time()
        response = requests.get(url_with_params)

        logging.info(f"Received response with status code: {response.status_code} for URL: {url_with_params} after {time() - start:.2f} seconds")
        if 200 <= response.status_code < 300:
            result_queue.put(response.json())
    except requests.RequestException as e:
        logging.error(f"Request to URL: {url_with_params} failed with exception: {e}")
        result_queue.put(None)


def get_first_successful_response(urls, n, params):
    result_queue = queue.Queue()
    threads = []
    for _ in range(n):
        for url in urls:
            t = threading.Thread(target=make_request, args=(url, params, result_queue))
            threads.append(t)   
            t.start()
    while True:
        result = result_queue.get()
        if result is not None:
            print(f"First non-null result: {result}")
            return result
        if all(not t.is_alive() for t in threads):
            break
    return None


@app.route('/manage/health', methods=['GET'])
def manage_health():
    return jsonify({"status": True}), 200


@app.route('/get', methods=['GET'])
def get_first_successful():
    n = int(os.getenv('NUM_REQUESTS', 3))
    urls_str = os.getenv('URLS', '')
    if not urls_str:
        return jsonify({'status': 'failed', 'message': 'URLs not provided in environment variables'}), 400

    urls = urls_str.split(',')
    params = request.args.to_dict()

    start_time = time()
    result = get_first_successful_response(urls, n, params)
    end_time = time()

    if result:
        return jsonify({
            'status': 'success',
            'data': result,
            'time_taken': round(end_time - start_time, 6)
        }), 200
    else:
        return jsonify({'status': 'failed', 'message': 'No successful response'}), 500

if __name__ == '__main__':
    app.run(debug=True)