# tester_bot.py

from flask import Flask, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import sys
import traceback

app = Flask(__name__)

# Initialize LLaMA 2 for code analysis
model_name = "meta-llama/Llama-2-7b-code-hf"  # Replace with your actual model path or identifier
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
model.eval()

# Security key (shared with Manager Bot)
API_KEY = "secure_manager_key"

# Endpoint to receive code for testing
@app.route('/test_code', methods=['POST'])
def test_code():
    key = request.headers.get('X-API-KEY')
    if key != API_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    code = request.json.get('code', '')
    language = request.json.get('language', '').lower()

    if not code or language != 'python':
        return jsonify({'status': 'error', 'message': 'Invalid code or language.'}), 400

    print("Received code for testing.")
    # Analyze code for correctness and completeness
    try:
        errors = analyze_code(code)
        if errors:
            print(f"Code has errors: {errors}")
            return jsonify({'status': 'error', 'errors': errors}), 200
        else:
            print("Code is correct.")
            return jsonify({'status': 'success', 'message': 'Code is correct.'}), 200
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Exception during code analysis: {error_msg}")
        return jsonify({'status': 'error', 'errors': str(e)}), 200

# Endpoint to receive tasks from Manager Bot (if needed)
@app.route('/task', methods=['POST'])
def handle_task():
    # Placeholder for handling other tasks if needed
    return jsonify({'status': 'success', 'message': 'Task received.'}), 200

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
        with open('tester_bot.py', 'w') as f:
            f.write(new_code)
        return jsonify({'status': 'success', 'message': 'Code updated successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def analyze_code(code):
    # Use LLaMA 2 to analyze the code for errors
    prompt = f"Analyze the following Python code for correctness and completeness. List any errors or issues:\n{code}"
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(inputs, max_length=512, num_return_sequences=1, temperature=0.5)
    analysis = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # If analysis contains 'No errors' or similar, return None
    if 'no errors' in analysis.lower() or 'code is correct' in analysis.lower():
        return None
    else:
        return analysis

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    app.run(port=port)
