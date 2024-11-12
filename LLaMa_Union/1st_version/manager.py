from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URLs of other bots
PROGRAMMER_BOT_URL = 'http://localhost:5001'
TEST_BOT_URL = 'http://localhost:5002'
DESIGNER_BOT_URL = 'http://localhost:5004'  # Updated if needed
SENTIMENT_ANALYZER_URL = 'http://localhost:5003'

# API keys for each bot
BOT_API_KEYS = {
    'programmer': 'programmer_secure_key',
    'test_bot': 'test_bot_secure_key',
    'designer': 'designer_secure_key',
    'sentiment_analyzer': 'sentiment_secure_key'
}

def authenticate(request, bot_name):
    key = request.headers.get('X-API-KEY')
    return key == BOT_API_KEYS.get(bot_name, '')

@app.route('/assign_task', methods=['POST'])
def assign_task():
    task = request.json
    task_type = task.get('type')
    data = task.get('data')

    headers = {}
    url = ''
    if task_type == 'update_code':
        headers['X-API-KEY'] = BOT_API_KEYS['programmer']
        url = f"{PROGRAMMER_BOT_URL}/update_code"
    elif task_type == 'run_tests':
        headers['X-API-KEY'] = BOT_API_KEYS['test_bot']
        url = f"{TEST_BOT_URL}/run_tests"
    elif task_type == 'generate_strategy':
        headers['X-API-KEY'] = BOT_API_KEYS['designer']
        url = f"{DESIGNER_BOT_URL}/generate_strategy"
    elif task_type == 'analyze_sentiment':
        headers['X-API-KEY'] = BOT_API_KEYS['sentiment_analyzer']
        url = f"{SENTIMENT_ANALYZER_URL}/analyze_sentiment"
    else:
        return jsonify({'status': 'error', 'message': 'Unknown task type'}), 400

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return jsonify({'status': 'success', 'response': response.json()}), 200
        else:
            return jsonify({'status': 'error', 'message': response.text}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/receive_update', methods=['POST'])
def receive_update():
    update = request.json
    # Handle updates from Programmer, Test, Designer, or Sentiment Analyzer Bots
    print(f"Received update: {update}")
    # Implement logic based on update
    return jsonify({'status': 'update received'}), 200

if __name__ == '__main__':
    app.run(port=5000)

