import pandas as pd
import numpy as np

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
         'SEASONYEAR', \
         'GAMEID', \
         'GAMEDATE', \
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

    # rename the columns to be more friendly
    pbp.columns = ['Quarter', \
                    'Minute', \
                    'Second', \
                    'OffenseTeam', \
                    'DefenseTeam', \
                    'Down', \
                    'ToGo', \
                    'YardLine', \
                    'Description', \
                    'Yards', \
                    'Formation', \
                    'PlayType', \
                    'IsRush', \
                    'IsPass', \
                    'PassType', \
                    'RushDirection', \
                    'YardLineFixed', \
                    'YardLineDirection']

    # get rid of all the kicks except punts and field goals
    pbp = pbp[(pbp.PlayType != 'KICK OFF') & (pbp.PlayType != 'EXTRA POINT') & \
              (pbp.PlayType != 'TWO-POINT CONVERSION')]

    # get rid of all the timeout plays
    pbp = pbp[pbp.OffenseTeam.notnull()]

    # get rid of all of the no-plays
    pbp = pbp[(pbp.PlayType != 'NO PLAY') & (pbp.PlayType != 'EXCEPTION') & \
              (pbp.PlayType != 'CLOCK STOP')& (pbp.PlayType != 'PENALTY')]

    # get rid of all the malformed pass types
    passtypes = ['DEEP MIDDLE', 'SHORT LEFT', 'SHORT RIGHT', 'SHORT MIDDLE', \
                 'DEEP LEFT', 'DEEP RIGHT']
    pbp = pbp[(pbp['PassType'].isin(passtypes)) | (pbp['PassType'].isnull())]

    # replace the nan PlayTypes with 'DIRECT SNAP'
    pbp.PlayType = pbp.PlayType.fillna('DIRECT SNAP')

    # drop the existing IsRush/IsPass and create new ones
    pbp.drop(['IsRush', 'IsPass'], axis=1, inplace=True)

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

    pbp['IsRush'] = pbp['PlayType'].map(play_to_rush)

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

    pbp['IsPass'] = pbp['PlayType'].map(play_to_pass)

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

    pbp['IsKick'] = pbp['PlayType'].map(play_to_kick)


    # Combine the dummy classes into one var and drop the dummies
    def play_type(x):
        if x.IsRush == 1:
            return 'RUSH'
        if x.IsPass == 1:
            return 'PASS'
        if x.IsKick == 1:
            return 'KICK'
        else:
            return 'NaN'

    pbp['Play'] = pbp.apply(lambda x: play_type(x), axis=1)

    pbp.drop(['IsRush', 'IsPass', 'IsKick'], axis=1, inplace=True)

    # Convert some columns to categorical
    pbp.Formation = pbp.Formation.astype("category")
    pbp.OffenseTeam = pbp.OffenseTeam.astype("category")
    pbp.DefenseTeam = pbp.DefenseTeam.astype("category")
    pbp.Play = pbp.Play.astype("category")

    return pbp

if __name__ == '__main__':

    # the 2013 data has some stray escaped quotes (\") that confuse pandas
    remove_inner_quotes('data/pbp-2013.csv', 'data/pbp-2013-fixed.csv')

    clean('data/pbp-2016.csv').to_csv('data/pbp2016-clean.csv', index=False)
    clean('data/pbp-2015.csv').to_csv('data/pbp2015-clean.csv', index=False)
    clean('data/pbp-2014.csv').to_csv('data/pbp2014-clean.csv', index=False)
    clean('data/pbp-2013-fixed.csv').to_csv('data/pbp2013-clean.csv', index=False)
