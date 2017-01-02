from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from resources.chart import Chart


app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(Chart, '/charts/<chart_id>')


def run():
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


if __name__ == '__main__':
    run()
