from flask import Flask, request, jsonify
import subprocess
import requests

app = Flask(__name__)

# Secure API key
API_KEY = 'test_bot_secure_key'


def authenticate(request):
    key = request.headers.get('X-API-KEY')
    return key == API_KEY


@app.route('/run_tests', methods=['POST'])
def run_tests():
    if not authenticate(request):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    # Example: Run pytest
    test_command = data.get('test_command', ['pytest', 'tests/'])

    try:
        result = subprocess.run(test_command, capture_output=True, text=True, check=True)
        # Notify Manager Bot about test results
        update_payload = {'status': 'tests passed', 'output': result.stdout}
        requests.post('http://localhost:5000/receive_update', json=update_payload)
        return jsonify({'status': 'tests passed', 'output': result.stdout}), 200
    except subprocess.CalledProcessError as e:
        update_payload = {'status': 'tests failed', 'output': e.stdout + e.stderr}
        requests.post('http://localhost:5000/receive_update', json=update_payload)
        return jsonify({'status': 'tests failed', 'output': e.stdout + e.stderr}), 400


if __name__ == '__main__':
    app.run(port=5002)
