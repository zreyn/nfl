import pandas as pd
import numpy as np

def combine(filenames):

    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    df = pd.concat(dfs)

    return df

def prep(df):

    # A few columns have to go for us to build a model (though we use them for user presentation)
    df.drop(['YardLineFixed', 'YardLineDirection','Description', 'PlayType', \
             'PassType', 'RushDirection', 'Yards', 'DefenseTeam'], axis=1, inplace=True)

    # create dummy variables for formations
    form_dummies = pd.get_dummies(df.Formation)
    form_dummies.columns = map(lambda x: 'FORMATION_' + x.replace (' ', '_'), form_dummies.columns)

    # create dummy variables for teams
    team_dummies = pd.get_dummies(df.OffenseTeam)
    team_dummies.columns = map(lambda x: 'TEAM_' + str(x), team_dummies.columns)

    # combine the dummy variables and drop the categorical versions
    df_prepped = pd.concat(
        [df.ix[:,['Quarter', 'Minute', 'Second', 'Down', 'ToGo', 'YardLine', 'Play']],
        team_dummies,
        form_dummies], axis=1)

    return df_prepped

if __name__ == '__main__':

    # read in the cleaned data and combine it
    filenames = ['data/pbp2015-clean.csv', 'data/pbp2014-clean.csv', 'data/pbp2013-clean.csv']
    pbp = combine(filenames)

    # prep the data for modeling and then save it to file
    prep(pbp).to_csv('data/pbp-prepped.csv', index=False)
