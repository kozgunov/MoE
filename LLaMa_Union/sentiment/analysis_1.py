from flask import Flask, request, jsonify
from transformers import LlamaTokenizer, LlamaForSequenceClassification
import torch

app = Flask(__name__)

# Load the fine-tuned model and tokenizer
model_name = 'llama-2-7b-sentiment'  # Path to your fine-tuned model
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = LlamaForSequenceClassification.from_pretrained(model_name)

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# API key for authentication
API_KEY = 'sentiment_secure_key'


def authenticate(request):
    key = request.headers.get('X-API-KEY')
    return key == API_KEY


@app.route('/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    if not authenticate(request):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Tokenize input
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    inputs = {key: val.to(device) for key, val in inputs.items()}

    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()

    # Map predicted class to sentiment
    sentiment = 'Positive' if predicted_class == 1 else 'Negative'

    return jsonify({'sentiment': sentiment}), 200


if __name__ == '__main__':
    app.run(port=5003)
