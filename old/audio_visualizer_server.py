from flask import Flask, render_template, Response, request
import os

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audio', methods=['POST'])
def process_audio():
    # Here you would receive the audio data from the front-end
    # and process it, but for this example, we are just returning a 200 OK response.
    return Response(status=200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
