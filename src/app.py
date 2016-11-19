'''
This is the main Flask web app for the project.

We can test out the server by:
1) Creating a model: python src/build_model.py
2) Testing the model: python src/test_model.py
3) Running the server: python src/app.py
4) Open home page with the browser: http://localhost:8080/
'''


'''
==================================
IMPORTS
==================================
'''
import cPickle as pickle
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
from modeling import prep_records
import socket
import requests
import time
import datetime
import copy
import random


'''
==================================
GLOBALS
==================================
'''
# register this as 'app'
app = Flask(__name__)

# load the current model
with open('data/gbc-v3.pkl', 'r') as f:
    model = pickle.load(f)

# set the model version
model_version = 'gbc-v3'

# for now, just use a file to store confusion matrices
user_cm_file = 'data/user_cm.csv'
model_cm_file = 'data/model_cm.csv'
cm_index_dict = {'PASS':0, 'RUSH':1, 'KICK':2}

# filename where the data is located
data_filename = 'data/pbp-validation.csv'

'''
==================================
HELPER FUNCTIONS
==================================
'''

def get_a_play():
    # grab a random record and prep it
    return pbp.iloc[random.randint(0, pbp.shape[0])].copy()

def predict(record):

    # prep the record for the model
    record_prepped = prep_records(pd.DataFrame(record).T)

    # split the class from the features
    y_one = record_prepped['Play']
    X_one = record_prepped.drop(['Play'], axis=1).values

    # run a predict and predict_proba to get the class and probabilities
    play_pred = model.predict(X_one)
    probas = model.predict_proba(X_one)

    return play_pred, probas

def create_confusion_matrices():

    # read them from a file
    user_cm = np.loadtxt(user_cm_file, delimiter=',')
    model_cm = np.loadtxt(model_cm_file, delimiter=',')

    #return model_confusion_matrix, user_confusion_matrix
    return user_cm, model_cm


def compute_accuracy(cm):

    # given a confusion matrix (y=true, x=pred), calculate accuracy
    num_right = 0
    for i in xrange(len(cm)):
        num_right += cm[i][i]

    # if none were right (or we have no data), return 0; otherwise return accuracy
    if num_right == 0:
        return 0
    else:
        return num_right / cm.sum()

'''
==================================
Flask methods
==================================
'''
# home page
@app.route('/')
def home_page():

    record = get_a_play()
    play_pred, probas = predict(record)

    # prep the data for the template
    data = {}
    data['record'] = record
    data['probas'] = probas[0]
    data['play_pred'] = play_pred[0]

    # pass the records to the template and render it
    return render_template('home.html', data=data)

# about the author page
@app.route('/author')
def author_page():

    data = {}

    # pass the records to the template and render it
    return render_template('author.html', data=data)

# about the project page
@app.route('/project')
def project_page():

    data = {}

    # pass the records to the template and render it
    return render_template('project.html', data=data)

# about the author page
@app.route('/field')
def field():

    data = {}

    # pass the records to the template and render it
    return render_template('field.html', data=data)


# get just the confusion matrices
@app.route('/get_accuracy')
def get_accuracy():

    # prep the data for the template
    data = {}
    data['model_version'] = model_version
    data['user_cm'] = user_cm.astype(int).tolist()
    data['model_cm'] = model_cm.astype(int).tolist()
    data['user_accuracy'] = compute_accuracy(user_cm)*100
    data['model_accuracy'] = compute_accuracy(model_cm)*100

    # pass the confusion matrices to the template and render it
    return render_template('accuracy.html', data=data)


# Log the user guesses.  Test with:
# curl -H "Content-Type: application/json" -X POST -d '@src/static/example.json' http://localhost:8080/guess
@app.route('/guess', methods=['POST'])
def guess():

    # pull the request data
    request_data = request.json

    # look up the right indices in the confusion matrices (y=true, x=pred)
    y = cm_index_dict[request_data['actual_play']]
    user_x = cm_index_dict[request_data['user_guess']]
    model_x = cm_index_dict[request_data['model_guess']]

    # update the proper cells
    user_cm[y][user_x] += 1
    model_cm[y][model_x] += 1

    # save out the confusion matrices (the user shouldn't be waiting for this)
    np.savetxt('data/user_cm.csv', user_cm, delimiter=',')
    np.savetxt('data/model_cm.csv', model_cm, delimiter=',')

    # respond with the updated aggregate stats (the two confusion matrices as json)
    return jsonify({'model_version':model_version})

'''
========================================================
If this is kicked from the command-line, run the server
========================================================
'''
if __name__ == '__main__':

    # read in the cleaned data
    pbp = pd.read_csv(data_filename)

    # read in the confusion matrix data
    user_cm, model_cm = create_confusion_matrices()

    # run the app
    app.run(host='0.0.0.0', port=8080, debug=False)
