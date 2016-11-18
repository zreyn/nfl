import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def combine(filenames):

    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    df = pd.concat(dfs)

    return df

def add_features(pbp, pbp_pfr):

    # for each play in our main dataframe, find the corresponding play in the other
    for play in pbp.iterrows():
        matching_play = pbp_pfr[
            (pbp_pfr['season'] == rand_play['SEASONYEAR']) &
            (pbp_pfr['quarter'] == rand_play['QUARTER']) &
            (pbp_pfr['minute'] == rand_play['MINUTE']) &
            (pbp_pfr['second'] == rand_play['SECOND']) &
            (pbp_pfr['down'] == rand_play['DOWN']) &
            (pbp_pfr['yds_to_go'] == rand_play['TOGO']) &
            (pbp_pfr['yardlinefixed'] == rand_play['YARDLINEFIXED'])
        ]

        # if we didn't get one exact match, we have to resolve it
        if len(matching_play.index) != 1:
            print 'Uh oh!', len(matching_play.index), 'matching records'
        else:
            #XXX do we have to create the new columns first? most likely

    return pbp

if __name__ == '__main__':

    # read in the cleaned NFL Savant data and combine it
    filenames = ['../data/pbp2016-clean.csv',
        '../data/pbp2015-clean.csv',
        '../data/pbp2014-clean.csv',
        '../data/pbp2013-clean.csv']
    pbp = combine(filenames)

    # read in the cleaned pro-football-reference data and combine it
    pbp_pfr = pd.read_csv('../data/pbp-pfr.csv')
    pbp = add_features(pbp, pbp_pfr)

    # split the data into a training and validation set (for the users and model to compete over)
    # 10% is about 13.5k plays
    pbp_train, pbp_validation = train_test_split(pbp, test_size = 0.1, random_state=22)

    # save the files
    pbp_train.to_csv('../data/pbp-training.csv', index=False)
    pbp_validation.to_csv('../data/pbp-validation.csv', index=False)
