from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import importlib
import threading
import time
import argparse
import json
import requests

app = Flask(__name__)
CORS(app)  # This enables CORS for all domains on all routes
baseAPI = "https://redteaming.virtueai.io"

@app.route('/testlocalchat', methods=['POST'])
def testlocalchat():
    data = request.get_json()  # Extract the JSON data from the request
    
    if data and 'message' in data and 'model' in data:
        user_message = data['message']
        model_name = data['model'][:-3]
        test_model = importlib.import_module(f'models.{model_name}')
        response = test_model.chat(user_message)  # Process the user message
        
        if response:
            # Successful response
            return jsonify(message=response, trigger=True), 200
        else:
            # Invalid request, message not provided
            return jsonify(message="No message provided", trigger=False), 400  # Bad Request
    else:
        return jsonify(message="Invalid request data", trigger=False), 400  # Bad Request
    


@app.route('/get_existing_models', methods=['GET'])
def get_existing_models():
    #  Define the path to the directory
    models_path = './models'
    # Initialize a list to hold file info
    model_files = []

    # Get files and their creation dates
    for f in os.listdir(models_path):
        full_path = os.path.join(models_path, f)
        if os.path.isfile(full_path):
            # Get the creation time and format it with time details
            creation_time = os.path.getctime(full_path)
            formatted_time = datetime.fromtimestamp(creation_time).strftime('%Y/%m/%d %H:%M:%S')
            # Append a tuple of file name and creation date to the list
            model_files.append((f, formatted_time))
            
    return jsonify(message=model_files, trigger=True), 200


def initialize_scan(scan_name, model_name):
    ScanUrl = baseAPI + "/scan_subcategory"
    
    data = {
        "userId": "test_user",  # Don't modify this
        "selectedDatasets": [
            {
                "name": "Fairness",
                "subcategories": ["Salary Prediction", "Crime Prediction"]
            }
        ],  # Don't modify this
        "scanName": scan_name,  # Replace with your chosen scan name
        "modelName": model_name,  # Replace with your model file name
        "clientAddress": "http://localhost:4410"  # Replace with your client address, don't modify the default port 4410
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(ScanUrl, json=data, headers=headers)

    if response.status_code == 200:
        print("Scan initialized successfully!")
        filename = response.json().get('filename')
        print(f"Filename: {filename}")
        return filename
    else:
        print(f"Scan initialization failed: {response.status_code}")
        print(response.text)
        return None

# Run the initialization


@app.route('/scan', methods=['POST'])
def scan():        
    data = request.get_json()
    scan_name = data.get('scan_name')
    model_name = data.get('model_name')
    filename = initialize_scan(scan_name, model_name)
    print("Save this filename to use in the status check and results retrieval.")
    return jsonify({'message': 'Scan started', 'trigger': True, 'filename': filename}), 200

@app.route('/check_scan_status', methods=['POST'])
def check_scan_status():
    data = request.get_json()
    filename = data.get('filename')
    CheckScanUrl = baseAPI + '/api/getreport'
    print('filename:', filename)
    data = {"filename": filename}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(CheckScanUrl, json=data, headers=headers)

    if response.status_code == 200:
        report_data = response.json()
        print(f"Scanning progress: {report_data.get('scanning_progress')}%")
        return jsonify({'message': f"Scanning progress: {report_data.get('scanning_progress')}%", 'trigger': True, 'filename': filename}), 200
    elif response.status_code == 400:
        print("Error: Filename not provided")        
    elif response.status_code == 404:
        print("Error: File not found")
    else:
        print(f"Status check failed: {response.status_code}")
        print(response.text)
    return jsonify({'message': 'Scan status checked', 'trigger': True, 'filename': filename}), 200

@app.route('/check_results', methods=['POST'])
def check_results(filename):
    resultUrl = baseAPI + f"/api/data/{filename}"
    
    response = requests.get(resultUrl)

    if response.status_code == 200:
        json_data = response.json()
        print("Run data summary:")
        print(f"Category scores: {json_data.get('averages')}")
        print(f"Subcategory scores: {json_data.get('averages_sub')}")
        print(f"Number of failure cases: {len(json_data.get('failures', []))}")
        print("Use json_data['scores'] for a detailed breakdown of results by risk levels.")
        print("Use json_data['failures'] to see the entire list of failure cases.")
        return json_data
    elif response.status_code == 404:
        print("Error: Run not found")
    else:
        print(f"Results retrieval failed: {response.status_code}")
        print(response.text)
        
    # Set the save path for the JSON file
    # Replace this with your desired file path and name
    save_path = "results.json"

    # Run the results check
    # If 'filename' is not defined, replace it with the actual filename from the initialization step
    json_data = check_results(filename)

    # Save the data if it was successfully retrieved
    if json_data:
        save_json_data(json_data, save_path)        
    return None

def save_json_data(data, save_path):
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {save_path}")
# Dictionary to store models and their last accessed time
models = {}
model_lock = threading.Lock()

class ModelWrapper:
    def __init__(self, model):
        self.model = model
        self.last_accessed = time.time()

def load_model(model_name):
    # model_module = importlib.import_module(f'models.{model_name[:-3]}')

    model_module = importlib.import_module(f'models.{model_name}')
    # if model_name.endswith('.py'):
    #     model_name = model_name[:-3]
    # model_module = importlib.import_module(f'models.{model_name}')
    importlib.reload(model_module)
    return model_module.chat

def get_model(process_id, model_name):
    with model_lock:
        if process_id not in models:
            models[process_id] = ModelWrapper(load_model(model_name))
        models[process_id].last_accessed = time.time()
        return models[process_id].model

def model_cleanup():
    while True:
        time.sleep(60)  # Check every minute
        with model_lock:
            for process_id, wrapper in list(models.items()):
                if time.time() - wrapper.last_accessed > 180:  # 3 minutes
                    del models[process_id]

cleanup_thread = threading.Thread(target=model_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt')
    process_id = data.get('process_id')
    model_name = data.get('model_name')
    finish_flag = data.get('finish_flag')
    
    model = get_model(process_id, model_name)
    
    try:
        answer = model(prompt)
        
        # If finish_flag is true, terminate the model process
        if finish_flag:
            with model_lock:
                if process_id in models:
                    del models[process_id]
        
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # from waitress import serve
    parser = argparse.ArgumentParser(description="Run the server with an optional port")
    parser.add_argument('--client_port', type=int, help='Client Port number', default=4410)
    args = parser.parse_args()
    
    
    print("Starting the Client")
    # print("Server is running on http://127.0.0.1:4399")
    # serve(app, host='0.0.0.0', port=4299)
    app.run(host='0.0.0.0',port=args.client_port, debug=True)