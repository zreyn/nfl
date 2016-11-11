'''
The purpose of this script is to load the pickle of a model and have it predict
a value.
'''

import cPickle as pickle
from build_model import DummyModel
import random

# load the model
with open('data/model.pkl') as f:
    model = pickle.load(f)

# read in the cleaned data and combine it
filenames = ['data/pbp2015-clean.csv', 'data/pbp2014-clean.csv', 'data/pbp2013-clean.csv']
pbp = combine(filenames)

# get a random record
record = get_a_play()

# send the data to the preprocessor, then to the model
play_pred, probas = predict(record)

print play_pred, probas

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
