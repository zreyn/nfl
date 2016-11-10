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


# get a random record

# send the data to the preprocessor

# send the data to the model and output results
