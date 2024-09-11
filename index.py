from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from application import AVM, translate
import subprocess
import os
import signal
import time
import psutil
from datetime import datetime
import numpy as np

app = Flask(__name__)

submitted_text = ""
npx_process = None

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/CHW-AVM")  # replace with your MongoDB URI
db = client['CHWDB']  # replace with your database name
collection = db['AVM']  # replace with your collection name

"""
# Compute TF-IDF vectors
documents = list(collection.find())
tfidf_vectorizer = TfidfVectorizer()
corpus = [doc['question'] + ' ' + doc['answer'] for doc in documents]
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
"""


def save_question_answer(question, answer):
    """
    document = {
        'question': question,
        'answer': answer,
        'timestamp': time.time()
    }
    collection.insert_one(document)
    # Update TF-IDF matrix
    global documents, tfidf_matrix, corpus
    documents.append(document)
    corpus.append(question + ' ' + answer)
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    """
    

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

@app.route('/submit', methods=['POST'])
def receive_data():
    global submitted_text
    data = request.get_json()
    submitted_text = data['text']
    print(submitted_text)
    var = AVM(submitted_text)
    save_question_answer(submitted_text, var)  # Save to MongoDB
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

@app.route('/results')
def results():
    documents = collection.find().sort('timestamp', -1)  # Get documents sorted by timestamp
    return render_template('results.html', documents=documents)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query:
        query_tfidf = tfidf_vectorizer.transform([query])
        cosine_similarities = np.dot(tfidf_matrix, query_tfidf.T).toarray().flatten()
        relevant_indices = cosine_similarities.argsort()[-10:][::-1]  # Get top 10 results
        relevant_docs = [documents[idx] for idx in relevant_indices]
    else:
        relevant_docs = documents
    
    results = [
        {
            "question": doc["question"], 
            "answer": doc["answer"], 
            "timestamp": datetimeformat(doc["timestamp"])
        } for doc in relevant_docs
    ]
    return jsonify(results)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return datetime.fromtimestamp(value).strftime(format)

if __name__ == '__main__':
    start_npx(port=1234)  # Start the npx process on port 1234 when the server starts
    app.run(debug=True)
