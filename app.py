from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from application import AVM, translate
import subprocess
import os
import signal
import time
import psutil

app = Flask(__name__)

# Setup MongoDB connection
mongo_uri = "mongodb+srv://mabhi02:AVMavmAVM@avmscluster.9vuoubd.mongodb.net/?retryWrites=true&w=majority&appName=AVMsCluster"

# Initialize MongoDB connection
client = MongoClient(mongo_uri)
db = client['myDatabase']
collection = db['questions']

submitted_text = ""
npx_process = None

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    proc.terminate()
                    proc.wait()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def start_npx(port=None):
    global npx_process
    if npx_process:
        npx_process.terminate()
        npx_process.wait()
    if port:
        kill_process_on_port(port)
        time.sleep(5)  # Wait for the port to be released
    command = ['npx', 'parcel', './src/index.html']
    if port:
        command += ['--port', str(port)]
    npx_process = subprocess.Popen(command, shell=True)
    time.sleep(5)  # Give it some time to start
    
def cut_string_to_100_chars(input_string):
    print(input_string)
    print("`````~~~~~~~~```````")
    return input_string[:100]

def save_question_answer(ui_prompt, response_quotes):
    """
    Save the question and its answer to MongoDB.
    """
    try:
        question_document = {
            "prompt": ui_prompt,
            "response": response_quotes
        }
        result = collection.insert_one(question_document)
        print(f"Document inserted with id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred while inserting the document: {e}")

@app.route('/submit', methods=['POST'])
def receive_data():
    global submitted_text
    data = request.get_json()
    submitted_text = data['text']
    print(submitted_text)
    var = AVM(submitted_text)
    # save_question_answer(submitted_text, var)
    shortened_string = cut_string_to_100_chars(var)
    print(shortened_string)
    try:
        translate(shortened_string)
    except AssertionError as e:
        print(f"Translation error: {e}")
        return jsonify({"status": "error", "message": "Translation failed"})
    start_npx()  # Restart without specifying port
    start_npx()  # Restart again without specifying port
    start_npx(port=1234)  # Final restart with port 1234
    print("~~~~~~Finished~~~~~~~~")
    return jsonify({"status": "success", "message": "Text received", "action": "click_center"})

@app.route('/')
def home():
    return render_template('stuff.html')

if __name__ == '__main__':
    start_npx(port=1234)  # Start the npx process on port 1234 when the server starts
    app.run(debug=True)
