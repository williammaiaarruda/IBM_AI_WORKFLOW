import argparse
import os
import re

import numpy as np
from flask import Flask, jsonify, request
from flask import render_template, send_from_directory

# import model specific functions and variables
from model import model_train, model_load, model_predict

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template('index.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/running', methods=['POST'])
def running():
    return render_template('running.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    basic predict function for the API
    """

    # input checking
    if not request.json:
        print("ERROR: API (predict): did not receive request data")
        return jsonify([])

    if 'country' not in request.json:
        print("ERROR API (predict): received request, but no 'country' found within")
        return jsonify([])
    
    if 'year' not in request.json:
        print("ERROR API (predict): received request, but no 'year' found within")
        return jsonify([])
    
    if 'month' not in request.json:
        print("ERROR API (predict): received request, but no 'month' found within")
        return jsonify([])
    
    if 'day' not in request.json:
        print("ERROR API (predict): received request, but no 'day' found within")
        return jsonify([])

    if 'type' not in request.json:
        print("WARNING API (predict): received request, but no 'type' was found assuming 'numpy'")
        query_type = 'numpy'

    # set the test flag
    test = False
    if 'mode' in request.json and request.json['mode'] == 'test':
        test = True

    # mount the query
    query = {'country': str(request.json['country']),
             'year': str(request.json['year']),
             'month': str(request.json['month']),
             'day': str(request.json['day'])
            }

    #if request.json['type'] == 'dict':
    #    pass
    #else:
    #    print("ERROR API (predict): only dict data types have been implemented")
    #    return jsonify([])

    # load model
    #_, model = model_load()
    production_data_dir = os.path.join("data", "cs-production")
    all_data, all_models = model_load(data_dir=production_data_dir)

    country = query['country']

    if not all_models:
        print("ERROR: model is not available")
        return jsonify([])

    if country not in all_models.keys():
        _result = {'ErrorMessage': "ERROR: model for country '{}' could not be found".format(country)}
    else:
        _result = model_predict(query, data=all_data[country], model=all_models[country], test=test)

    result = {}

    # convert numpy objects to ensure they are serializable
    for key, item in _result.items():
        if isinstance(item, np.ndarray):
            result[key] = item.tolist()
        else:
            result[key] = item

    print('predict end_point result: ', result)
    return jsonify(result)


@app.route('/train', methods=['GET', 'POST'])
def train():
    """
    basic predict function for the API

    the 'mode' flag provides the ability to toggle between a test version and a 
    production version of training
    """

    # check for request data
    if not request.json:
        print("ERROR: API (train): did not receive request data")
        return jsonify(False)

    # set the test flag
    test = False
    if 'mode' in request.json and request.json['mode'] == 'test':
        print('... test mode = true')
        test = True

    print("... training model")
    data_dir = os.path.join("data", "cs-train")
    model = model_train(data_dir, test=test)
    print("... training complete")

    return jsonify(True)


@app.route('/logs/<filename>', methods=['GET'])
def logs(filename):
    """
    API endpoint to get logs
    url: localhost:8080/logs/predict-test.log
    """

    if not re.search(".log", filename):
        print("ERROR: API (log): file requested was not a log file: {}".format(filename))
        return jsonify([])

    log_dir = os.path.join(".", "logs")
    if not os.path.isdir(log_dir):
        print("ERROR: API (log): cannot find log dir")
        return jsonify([])

    file_path = os.path.join(log_dir, filename)
    if not os.path.exists(file_path):
        print("ERROR: API (log): file requested could not be found: {}".format(filename))
        return jsonify([])

    return send_from_directory(log_dir, filename, as_attachment=True)


if __name__ == '__main__':

    # parse arguments for debug mode
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--debug", action="store_true", help="debug flask")
    args = vars(ap.parse_args())

    if args["debug"]:
        app.run(debug=True, port=8080)
    else:
        app.run(host='0.0.0.0', threaded=True, port=8080)
