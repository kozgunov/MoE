# javascript_bot.py

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys

app = Flask(__name__)

# Initialize LLaMA 2 for JavaScript code generation
model_name = "meta-llama/Llama-2-7b-code-hf"  # Replace with your actual model path or identifier
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Security key (shared with Manager Bot)
API_KEY = "secure_manager_key"

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

    if task_type != 'generate_code' or language != 'javascript' or not description:
        return jsonify({'status': 'error', 'message': 'Invalid task parameters.'}), 400

    # Generate JavaScript code using LLaMA 2
    code = generate_code(description)
    return jsonify({'status': 'success', 'result': code}), 200

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
        with open('javascript_bot.py', 'w') as f:
            f.write(new_code)
        return jsonify({'status': 'success', 'message': 'Code updated successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_code(description):
    prompt = f"Write a JavaScript function to {description}"
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(
        inputs,
        max_length=512,
        num_return_sequences=1,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )
    code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return code

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5002
    app.run(port=port)
