from flask import Flask, jsonify, request
import requests
import os
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)

def make_request(url, params):
    try:
        if params:
            url_with_params = f"{url}?{urlencode(params)}"
        else:
            url_with_params = url

        logging.info(f"Making request to URL: {url_with_params}")
        response = requests.get(url_with_params)

        logging.info(f"Received response with status code: {response.status_code} for URL: {url_with_params}")
        if response.status_code == 200:
            return response.json()
    except requests.RequestException as e:
        logging.error(f"Request to URL: {url_with_params} failed with exception: {e}")
        return None

    return None

def get_first_successful_response(urls, n, params):
    with ThreadPoolExecutor() as executor:
        futures = []
        for _ in range(n):
            for url in urls:
                futures.append(executor.submit(make_request, url, params))

        for future in as_completed(futures):
            result = future.result()
            if result:
                return result

    return None

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
            'response': result,
            'time_taken': end_time - start_time
        }), 200
    else:
        return jsonify({'status': 'failed', 'message': 'No successful response'}), 500

if __name__ == '__main__':
    app.run(debug=True)