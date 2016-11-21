import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import cPickle as pickle
import random

columns_to_keep = [
    'QUARTER',
    'MINUTE',
    'SECOND',
    'DOWN',
    'TOGO',
    'YARDLINE',
    'SCORINGMARGIN',
    'ISTURF',
    'UNDERROOF',
    'ISATHOME',
    'TEMPERATURE',
    'HUMIDITY',
    'WINDSPEED',
    'PLAY']

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

def prep_records(records, columns_to_keep=columns_to_keep, offense=True, formation=True):
    '''
    INPUT: records - a set of plays as rows in a DataFrame in "clean form"
           columns_to_keep - the list of columns to keep in the result
           offense - True=Dummies for the offense, False=no offense feature
           formation - True=Dummies for the formation, False=no formation feature
    OUTPUT: The plays in "model form"
    '''

    # Fill missing values for HUMIDITY, TEMPERATURE, WINDSPEED and convert to int
    records.TEMPERATURE = records.TEMPERATURE.replace('UNKOWN', '75') # typo in earlier script
    records.HUMIDITY = records.HUMIDITY.replace('UNKNOWN', '45')
    records.WINDSPEED = records.WINDSPEED.replace('UNKNOWN', '0')
    records.WINDSPEED = records.WINDSPEED.replace('wind', '0') # odd parsing from earlier
    records.TEMPERATURE = records.TEMPERATURE.astype("int")
    records.HUMIDITY = records.HUMIDITY.astype("int")
    records.WINDSPEED = records.WINDSPEED.astype("int")

    # Map the class to integer
    records['PLAY'] = records['PLAY'].map({'KICK':0, 'PASS':1, 'RUSH':2})

    # Dummy the team
    if offense:
        df2 = pd.get_dummies(records.OFFENSETEAM)
        dummies_frame = pd.get_dummies(teams)
        df2 = df2.reindex(columns=dummies_frame.columns, fill_value=0)
        df2.columns = map(lambda x: 'TEAM_' + str(x), df2.columns)

    # Dummy the formation
    if formation:
        df1 = pd.get_dummies(records.FORMATION)
        dummies_frame = pd.get_dummies(formations)
        df1 = df1.reindex(columns=dummies_frame.columns, fill_value=0)
        df1.columns = map(lambda x: 'FORMATION_' + x.replace (' ', '_'), df1.columns)

    # combine the dummy variables with any other column we're keeping
    if (offense and formation):
        records = pd.concat(
            [records.ix[:,columns_to_keep],
            df2,
            df1], axis=1)
    elif offense:
        records = pd.concat(
            [records.ix[:,columns_to_keep],
            df2], axis=1)
    elif formation:
        records = pd.concat(
            [records.ix[:,columns_to_keep],
            df1], axis=1)
    else:
        records = pd.concat(
            [records.ix[:,columns_to_keep]], axis=1)

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
    model = create_model(prep_records(data, columns_to_keep))

    # save the model
    with open('../data/'+model_name+'.pkl', 'w') as f:
        pickle.dump(model, f)
