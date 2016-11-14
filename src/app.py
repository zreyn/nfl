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
from flask import Flask, render_template, request, jsonify
from build_model import DummyModel
from create_training_data import combine, prep_record
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
with open('data/model.pkl', 'r') as f:
    model = pickle.load(f)

# set the model version
model_version = 'gdbc_v1'

# for now, just use a file to store confusion matrices
user_cm_file = 'data/user_cm.csv'
model_cm_file = 'data/model_cm.csv'
cm_index_dict = {'PASS':0, 'RUSH':1, 'KICK':2}

# read in the cleaned data and combine it
filenames = ['data/pbp2015-clean.csv', 'data/pbp2014-clean.csv', 'data/pbp2013-clean.csv']
pbp = combine(filenames)

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
    record_prepped = prep_record(pd.DataFrame(record).T)

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

def update_confusion_matrices(one_round):

    # look up the right indices in the confusion matrices (y=true, x=pred)
    y = cm_index_dict[one_round['actual_play']]
    user_x = cm_index_dict[one_round['user_guess']]
    model_x = cm_index_dict[one_round['model_guess']]

    # update the proper cells
    user_cm[y][user_x] += 1
    model_cm[y][model_x] += 1

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

# Log the user guesses.  Test with:
# curl -H "Content-Type: application/json" -X POST -d '@example.json' http://localhost:8080/guess
@app.route('/guess', methods=['POST'])
def guess():

    # pull the request and grab a timestamp and generate an id
    request_data = request.json
    timestamp = datetime.datetime.utcnow()
    record_id = str(int(round(time.time() * 1000)))

    # insert the score into the DB
    record = {
        '_id':record_id,
        'model_version':model_version,
        'actual_play':request_data['actual_play'],
        'model_guess':request_data['model_guess'],
        'user_guess':request_data['user_guess']
    }

    try:
        guesses_table.insert(record)
    except DuplicateKeyError:
        print 'Duplicate!'

    # update our risk counts
    update_confusion_matrices(request_data)

    # respond with the score
    # XXX need to return the two confusion matrices as JSON
    return jsonify({'model_version':model_version, })

'''
========================================================
If this is kicked from the command-line, run the server
========================================================
'''
if __name__ == '__main__':
    model_confusion_matrix, user_confusion_matrix = create_confusion_matrices()
    app.run(host='0.0.0.0', port=8080, debug=False)
