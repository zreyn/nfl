import pandas as pd
import numpy as np
import os

def remove_inner_quotes(infile, outfile):
    with open(outfile, 'wt') as fout:
        with open(infile, 'rt') as fin:
            for line in fin:
                fout.write(line.replace('\\"', ''))

def clean(filename):
    '''
    This function takes one of the nflsavant.com csv files and cleans it up by
    removing extraneous columns, normalizing the column names, remapping and
    computing values, etc.
    '''

    pbp = pd.read_csv(filename)

    # convert column names to upper case (since they are inconsistent in the data by season)
    pbp.columns = [x.upper() for x in pbp.columns]

    # drop all columns with no info, we won't use, or aren't in all the data
    pbp.drop(
        ['UNNAMED: 10', \
         'UNNAMED: 12', \
         'UNNAMED: 16',\
         'UNNAMED: 17', \
         'CHALLENGER', \
         'ISMEASUREMENT', \
         'NEXTSCORE', \
         'TEAMWIN',\
         'ISINCOMPLETE', \
         'ISTOUCHDOWN', \
         'ISSACK', \
         'ISCHALLENGE', \
         'ISCHALLENGEREVERSED', \
         'ISINTERCEPTION', \
         'ISPENALTY', \
         'ISTWOPOINTCONVERSION', \
         'SERIESFIRSTDOWN', \
         'ISTWOPOINTCONVERSIONSUCCESSFUL', \
         'ISPENALTYACCEPTED', \
         'PENALTYTEAM', \
         'ISFUMBLE', \
         'PENALTYTYPE', \
         'PENALTYYARDS', \
         'ISNOPLAY', \
         'DEFENSESCORE',
         'ISMESUREMENT',
         'ISPRESEASON',
         'OFFENSESCORE',
         'PENALIZEDPLAYER',
         'PLAYID',
         'SCORECHANGE',
         'SCOREDIFF'], \
          axis=1, inplace=True,  errors='ignore')

    # get rid of all the kicks except punts and field goals
    pbp = pbp[(pbp.PLAYTYPE != 'KICK OFF') & (pbp.PLAYTYPE != 'EXTRA POINT') & \
              (pbp.PLAYTYPE != 'TWO-POINT CONVERSION')]

    # get rid of all the timeout plays
    pbp = pbp[pbp.OFFENSETEAM.notnull()]

    # get rid of all of the no-plays
    pbp = pbp[(pbp.PLAYTYPE != 'NO PLAY') & (pbp.PLAYTYPE != 'EXCEPTION') & \
              (pbp.PLAYTYPE != 'CLOCK STOP')& (pbp.PLAYTYPE != 'PENALTY')]

    # get rid of all the malformed pass types
    passtypes = ['DEEP MIDDLE', 'SHORT LEFT', 'SHORT RIGHT', 'SHORT MIDDLE', \
                 'DEEP LEFT', 'DEEP RIGHT']
    pbp = pbp[(pbp['PASSTYPE'].isin(passtypes)) | (pbp['PASSTYPE'].isnull())]

    # replace the nan PlayTypes with 'DIRECT SNAP'
    pbp.PLAYTYPE = pbp.PLAYTYPE.fillna('DIRECT SNAP')

    # drop the existing IsRush/IsPass and create new ones
    pbp.drop(['ISRUSH', 'ISPASS'], axis=1, inplace=True)

    play_to_rush = {
        'RUSH': 1,
        'PASS' : 0,
        'PUNT' : 0,
        'QB KNEEL' : 1,
        'SCRAMBLE' : 0,
        'FIELD GOAL' : 0,
        'SACK' : 0,
        'FUMBLES' : 1,
        'DIRECT SNAP' : 1
    }

    pbp['ISRUSH'] = pbp['PLAYTYPE'].map(play_to_rush)

    play_to_pass = {
        'RUSH': 0,
        'PASS' : 1,
        'PUNT' : 0,
        'QB KNEEL' : 0,
        'SCRAMBLE' : 1,
        'FIELD GOAL' : 0,
        'SACK' : 1,
        'FUMBLES' : 0,
        'DIRECT SNAP' : 0
    }

    pbp['ISPASS'] = pbp['PLAYTYPE'].map(play_to_pass)

    play_to_kick = {
        'RUSH': 0,
        'PASS' : 0,
        'PUNT' : 1,
        'QB KNEEL' : 0,
        'SCRAMBLE' : 0,
        'FIELD GOAL' : 1,
        'SACK' : 0,
        'FUMBLES' : 0,
        'DIRECT SNAP' : 0
    }

    pbp['ISKICK'] = pbp['PLAYTYPE'].map(play_to_kick)


    # Combine the dummy classes into one var and drop the dummies
    def play_type(x):
        if x.ISRUSH == 1:
            return 'RUSH'
        if x.ISPASS == 1:
            return 'PASS'
        if x.ISKICK == 1:
            return 'KICK'
        else:
            return 'NaN'

    pbp['PLAY'] = pbp.apply(lambda x: play_type(x), axis=1)

    pbp.drop(['ISRUSH', 'ISPASS', 'ISKICK'], axis=1, inplace=True)

    # Convert some columns to categorical
    pbp.FORMATION = pbp.FORMATION.astype("category")
    pbp.OFFENSETEAM = pbp.OFFENSETEAM.astype("category")
    pbp.DEFENSETEAM = pbp.DEFENSETEAM.astype("category")
    pbp.PLAY = pbp.PLAY.astype("category")

    return pbp

if __name__ == '__main__':

    # the 2013 data has some stray escaped quotes (\") that confuse pandas
    raw_2013_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2013.csv')
    fixed_2013_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2013-fixed.csv')
    remove_inner_quotes(raw_2013_filename, fixed_2013_filename)

    raw_2016_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2016.csv')
    raw_2015_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2015.csv')
    raw_2014_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2014.csv')

    clean_2016_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2016.csv')
    clean_2015_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2015.csv')
    clean_2014_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2014.csv')
    clean_2013_filename = os.path.join(os.path.dirname(__file__), '../data/pbp-2013.csv')

    clean(raw_2016_filename).to_csv(clean_2013_filename, index=False)
    clean(raw_2015_filename).to_csv(clean_2014_filename, index=False)
    clean(raw_2014_filename).to_csv(clean_2015_filename, index=False)
    clean(fixed_2013_filename).to_csv(clean_2013_filename, index=False)
