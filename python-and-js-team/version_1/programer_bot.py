# programmer_bot.py

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys
import requests

app = Flask(__name__)

# Initialize LLaMA 2 for code generation
model_name = "meta-llama/Llama-2-7b-code-hf"  # Replace with your actual model path or identifier
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
model.eval()

# Security key (shared with Manager Bot)
API_KEY = "secure_manager_key"

# Tester Bot URL
TESTER_BOT_URL = "http://localhost:5003"  # Port where Tester Bot is running

# Endpoint to receive tasks
@app.route('/task', methods=['POST'])
def handle_task():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    task = request.json.get('task', {})
    task_type = task.get('task_type', '')
    language = task.get('language', '').lower()
    description = task.get('description', '')

    if task_type != 'generate_code' or language != 'python' or not description:
        return jsonify({'status': 'error', 'message': 'Invalid task parameters.'}), 400

    print(f"Received task: {description}")
    # Parse task using LLaMA 2 to ensure understanding
    parsed_task = parse_task(description)
    print(f"Parsed task: {parsed_task}")

    # Generate Python code using LLaMA 2
    code = generate_code(parsed_task)
    print("Generated code. Sending to Tester Bot for validation.")

    # Loop to fix code up to 5 times
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        attempts += 1
        print(f"Attempt {attempts} to validate code.")
        # Send code to Tester Bot
        test_result = send_code_to_tester(code, language)
        if test_result.get('status') == 'success':
            print("Code passed testing.")
            # Code is correct, send to Manager Bot
            return jsonify({'status': 'success', 'result': code, 'message': 'Code has been tested and is correct.'}), 200
        else:
            # There are errors, need to fix code
            errors = test_result.get('errors', '')
            print(f"Tester Bot found errors: {errors}")
            if attempts < max_attempts:
                # Use LLaMA 2 to fix code based on errors
                code = fix_code(code, errors)
                print("Code has been updated based on Tester Bot feedback.")
            else:
                # Max attempts reached, inform Manager Bot
                error_message = f"Failed to produce correct code after {max_attempts} attempts. Errors: {errors}"
                print(error_message)
                return jsonify({'status': 'error', 'message': error_message}), 200  # Return 200 so Manager can process

# Endpoint to modify code (for Manager Bot)
@app.route('/modify_code', methods=['POST'])
def modify_code():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    new_code = request.json.get('new_code', '')
    if not new_code:
        return jsonify({'status': 'error', 'message': 'No new code provided.'}), 400

    # Modify the bot's code (overwrite the current script)
    try:
        with open('programmer_bot.py', 'w') as f:
            f.write(new_code)
        return jsonify({'status': 'success', 'message': 'Code updated successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def parse_task(description):
    # Use LLaMA 2 to parse and understand the task
    prompt = f"Understand and rephrase the following task: {description}"
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(inputs, max_length=256, num_return_sequences=1, temperature=0.7)
    parsed_description = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return parsed_description

def generate_code(description):
    prompt = f"Write a Python script to {description}"
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(inputs, max_length=512, num_return_sequences=1, temperature=0.7)
    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return code

def send_code_to_tester(code, language):
    try:
        url = f"{TESTER_BOT_URL}/test_code"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': API_KEY}
        response = requests.post(url, json={'code': code, 'language': language}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error communicating with Tester Bot: {response.status_code}")
            return {'status': 'error', 'errors': 'Communication error with Tester Bot.'}
    except Exception as e:
        print(f"Exception occurred while sending code to Tester Bot: {e}")
        return {'status': 'error', 'errors': str(e)}

def fix_code(code, errors):
    # Use LLaMA 2 to fix code based on errors
    prompt = f"The following Python code has errors:\n{code}\nErrors:\n{errors}\nPlease provide a corrected version of the code."
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(inputs, max_length=512, num_return_sequences=1, temperature=0.7)
    fixed_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return fixed_code

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(port=port)
