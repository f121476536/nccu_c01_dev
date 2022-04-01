#API相關
import flask
from flask import jsonify, request
from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JSON_AS_ASCII"] = False
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello World~!</h1>"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8871)