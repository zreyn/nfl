import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import cPickle as pickle
import random

class DummyModel(object):

    def predict_proba(self, X):
        return random.random()

def create_model(df_prepped):

    # for a dummy model
    #return DummyModel()

    # split the class from the values
    y = df_prepped['Play']
    X = df_prepped.drop(['Play'], axis=1).values

    # use all of the data, the validation set will come from unseen data
    gbc = GradientBoostingClassifier()
    gbc.fit(X, y)

    return gbc

def read_data(filename):
    return pd.read_csv(filename)

if __name__ == '__main__':

    # read in the prepped data
    data = read_data('../data/pbp-training.csv')

    # name the model
    model_name = 'gbc-v4'

    # create the model
    model = create_model(data)

    # save the model
    with open('../data/'+model_name+'.pkl', 'w') as f:
        pickle.dump(model, f)
