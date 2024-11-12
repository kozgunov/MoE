from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Secure API key
API_KEY = 'programmer_secure_key'

def authenticate(request):
    key = request.headers.get('X-API-KEY')
    return key == API_KEY

@app.route('/update_code', methods=['POST'])
def update_code():
    if not authenticate(request):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json
    # Example: Pull latest code from repository
    repo_url = data.get('repo_url')
    branch = data.get('branch', 'main')

    try:
        # Pull the latest code
        subprocess.run(['git', 'pull', repo_url, branch], check=True)
        # Optionally, restart services or perform additional steps
        # subprocess.run(['systemctl', 'restart', 'trading_service'], check=True)
        # Notify Manager Bot about the update
        # This requires the Manager Bot to expose an endpoint to receive updates
        # Example:
        # requests.post('http://localhost:5000/receive_update', json={'status': 'code updated'})
        return jsonify({'status': 'code updated successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)

