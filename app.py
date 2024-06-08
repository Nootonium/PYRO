from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from resources import DocumentProcessorResource

app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)
api.add_resource(DocumentProcessorResource, '/extract/<string:object_key>')


@app.route('/ping')
def ping():
    return "Pong"

if __name__ == '__main__':
    app.run(debug=True)
