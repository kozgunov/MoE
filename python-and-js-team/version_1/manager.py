# just input python manager.py

#  I need a Python script that calculates the factorial of a number.
#  Test the factorial Python script.
# I need a JavaScript function that reverses a string.
# Generate a new idea for a cryptocurrency trading bot.
#{
#  "task_type": "generate_code",
#  "language": "python",
#  "description": "calculate the factorial of a number"
#}

# manager.py

import threading
import subprocess
import requests
import time
from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

# Define ports for each bot
BOTS = {
    'programmer': 5001,
    'javascript': 5002,
    'tester': 5003,
    'designer': 5004
}

# API key for security
API_KEY = "secure_manager_key"

# General Chat Log
general_chat = []

# Function to start each bot
def start_bot(bot_name, script_name, port):
    def run_bot():
        subprocess.run(['python', script_name, str(port)])
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    print(f"{bot_name.capitalize()} Bot started on port {port}")
    return thread

# Start all bots
def launch_bots():
    threads = []
    threads.append(start_bot('programmer', 'programmer_bot.py', BOTS['programmer']))
    threads.append(start_bot('javascript', 'javascript_bot.py', BOTS['javascript']))
    threads.append(start_bot('tester', 'tester_bot.py', BOTS['tester']))
    threads.append(start_bot('designer', 'creative_designer_bot.py', BOTS['designer']))
    return threads

# Authenticate incoming requests
def authenticate(request):
    key = request.headers.get('X-API-KEY')
    return key == API_KEY

# Endpoint to receive updates from bots
@app.route('/receive_update', methods=['POST'])
def receive_update():
    if not authenticate(request):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    update = request.json
    bot_name = update.get('bot', 'Unknown')
    message = update.get('message', '')
    general_chat.append(f"{bot_name.capitalize()} Bot: {message}")
    print(f"{bot_name.capitalize()} Bot: {message}")
    return jsonify({'status': 'update received'}), 200

# Endpoint to get general chat
@app.route('/general_chat', methods=['GET'])
def get_general_chat():
    if not authenticate(request):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    return jsonify({'general_chat': general_chat}), 200

# Function to delegate tasks
def delegate_task(task_type, task_data):
    if task_type == 'modify_code':
        # Modify code of a specific bot
        target_bot = task_data.get('bot')
        new_code = task_data.get('new_code')
        if target_bot in BOTS:
            url = f"http://localhost:{BOTS[target_bot]}/modify_code"
            headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}
            response = requests.post(url, json={'new_code': new_code}, headers=headers)
            if response.status_code == 200:
                message = f"Code of {target_bot.capitalize()} Bot updated successfully."
                general_chat.append(f"Manager: {message}")
                print(message)
            else:
                message = f"Failed to update code of {target_bot.capitalize()} Bot."
                general_chat.append(f"Manager: {message}")
                print(message)
        else:
            message = f"Unknown bot: {target_bot}"
            general_chat.append(f"Manager: {message}")
            print(message)
    else:
        # Delegate to appropriate bot
        bot_map = {
            'python_task': 'programmer',
            'javascript_task': 'javascript',
            'test_task': 'tester',
            'design_task': 'designer'
        }
        bot_name = bot_map.get(task_type)
        if bot_name:
            url = f"http://localhost:{BOTS[bot_name]}/task"
            headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}
            response = requests.post(url, json={'task': task_data}, headers=headers)
            if response.status_code == 200:
                resp_json = response.json()
                status = resp_json.get('status')
                if status == 'success':
                    result = resp_json.get('result', '')
                    message = resp_json.get('message', '')
                    general_chat.append(f"{bot_name.capitalize()} Bot: {message}\n{result}")
                    print(f"{bot_name.capitalize()} Bot: {message}\n{result}")
                elif status == 'error':
                    error_message = resp_json.get('message', '')
                    general_chat.append(f"{bot_name.capitalize()} Bot Error: {error_message}")
                    print(f"{bot_name.capitalize()} Bot Error: {error_message}")
                else:
                    general_chat.append(f"{bot_name.capitalize()} Bot: Unknown response.")
                    print(f"{bot_name.capitalize()} Bot: Unknown response.")
            else:
                message = f"Failed to delegate task to {bot_name.capitalize()} Bot."
                general_chat.append(f"Manager: {message}")
                print(message)
        else:
            message = f"Unknown task type: {task_type}"
            general_chat.append(f"Manager: {message}")
            print(message)

# Function to handle user input
def user_input_handler():
    while True:
        try:
            user_input = input("\nEnter task (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Shutting down Manager and all bots...")
                sys.exit(0)
            elif user_input.startswith("modify"):
                # Example command: modify <bot_name> <new_code>
                parts = user_input.split(' ', 2)
                if len(parts) == 3:
                    _, bot_name, new_code = parts
                    task_data = {'bot': bot_name, 'new_code': new_code}
                    delegate_task('modify_code', task_data)
                else:
                    print("Invalid modify command. Use: modify <bot_name> <new_code>")
            else:
                # Determine task type based on input
                task_type = 'python_task'  # Default task
                language = 'python'
                if 'python' in user_input.lower():
                    task_type = 'python_task'
                    language = 'python'
                elif 'javascript' in user_input.lower():
                    task_type = 'javascript_task'
                    language = 'javascript'
                elif 'test' in user_input.lower():
                    task_type = 'test_task'
                elif 'idea' in user_input.lower() or 'design' in user_input.lower():
                    task_type = 'design_task'
                else:
                    task_type = 'python_task'
                    language = 'python'
                if task_type in ['python_task', 'javascript_task']:
                    task_data = {
                        'task_type': 'generate_code',
                        'language': language,
                        'description': user_input
                    }
                else:
                    task_data = {
                        'task_type': 'general_task',
                        'description': user_input
                    }
                delegate_task(task_type, task_data)
        except EOFError:
            break

if __name__ == '__main__':
    # Launch bots
    launch_bots()
    time.sleep(5)  # Wait for bots to start

    # Start Flask server in a separate thread
    server_thread = threading.Thread(target=lambda: app.run(port=5000))
    server_thread.daemon = True
    server_thread.start()

    # Start user input handler
    user_input_handler()
