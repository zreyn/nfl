import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import cPickle as pickle
import random

columns_to_keep = ['QUARTER', 'MINUTE', 'SECOND', 'DOWN', 'TOGO', 'YARDLINE', 'PLAY']

formations = [
'FIELD_GOAL',
'NO_HUDDLE',
'NO_HUDDLE_SHOTGUN',
'PUNT',
'SHOTGUN',
'UNDER_CENTER',
'WILDCAT']

teams = [
'ARI',
'ATL',
'BAL',
'BUF',
'CAR',
'CHI',
'CIN',
'CLE',
'DAL',
'DEN',
'DET',
'GB',
'HOU',
'IND',
'JAX',
'KC',
'LA',
'MIA',
'MIN',
'NE',
'NO',
'NYG',
'NYJ',
'OAK',
'PHI',
'PIT',
'SD',
'SEA',
'SF',
'TB',
'TEN',
'WAS']

def prep_records(records):
    '''
    INPUT: A set of plays as rows in a DataFrame in "clean form"
    OUTPUT: The plays in "model form"
    '''

    # Dummy the team
    df2 = pd.get_dummies(records.OFFENSETEAM)
    dummies_frame = pd.get_dummies(teams)
    df2 = df2.reindex(columns=dummies_frame.columns, fill_value=0)
    df2.columns = map(lambda x: 'TEAM_' + str(x), df2.columns)

    # Dummy the formation
    df1 = pd.get_dummies(records.FORMATION)
    dummies_frame = pd.get_dummies(formations)
    df1 = df1.reindex(columns=dummies_frame.columns, fill_value=0)
    df1.columns = map(lambda x: 'FORMATION_' + x.replace (' ', '_'), df1.columns)

    # combine the dummy variables with any other column we're keeping
    records = pd.concat(
        [records.ix[:,columns_to_keep],
        df2,
        df1], axis=1)

    return records

def create_model(df_prepped):

    # split the class from the values
    y = df_prepped['PLAY']
    X = df_prepped.drop(['PLAY'], axis=1).values

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

    # prep the data and create the model
    model = create_model(prep_records(data))

    # save the model
    with open('../data/'+model_name+'.pkl', 'w') as f:
        pickle.dump(model, f)
