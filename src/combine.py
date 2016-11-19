import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def combine(filenames):

    dfs = []
    for filename in filenames:
        dfs.append(pd.read_csv(filename))

    df = pd.concat(dfs)

    return df

def parse_weather(wstring):
    '''
    INPUT: A game weather string scraped from pro-football-reference.com
    OUTPUT: dict{'TEMPERATURE':(F degrees), 'HUMIDITY': (%), 'WINDSPEED': (mph)}

    Example inputs:
    '36 degrees relative humidity 91%, wind 16 mph, wind chill 26',
    '37 degrees relative humidity 39%, wind 2 mph',
    '37 degrees relative humidity 56%, no wind',
    '''

    ret_values = {}
    ret_values['TEMPERATURE'] = 'UNKOWN'
    ret_values['HUMIDITY'] = 'UNKNOWN'
    ret_values['WINDSPEED'] = 'UNKNOWN'

    # if the value was missing, propagate that back
    if wstring == 'UNKNOWN':
        return ret_values

    # add a comma between temp and humidity to make the parts cleaner
    wstring = wstring.replace('degrees relative', 'degrees, relative')

    # split into parts
    parts = wstring.split(',')

    # part 0 is the temperature
    ret_values['TEMPERATURE'] = parts[0].split()[0]

    # part 1 is the humidity
    ret_values['HUMIDITY'] = parts[1][:-1].split()[-1]

    # part 3 is the windspeed
    if parts[2] == 'no wind':
        ret_values['WINDSPEED'] = '0'
    else:
        ret_values['WINDSPEED'] = parts[2].split()[1]

    # sometimes, there's a part 4, which is wind chill, but we will ignore that for now

    return ret_values

def compute_margin(play):
    if play['ISATHOME'] == 1:
        return play['HOMESCORE'] - play['AWAYSCORE']
    else:
        return play['AWAYSCORE'] - play['HOMESCORE']

def join(play, df1, df2):
    matching_play = df2[
            (df2['game_id'].str.contains(str(play['GAMEID'])[:8])) &
            (df2['quarter'] == play['QUARTER']) &
            (df2['minute'] == play['MINUTE']) &
            (df2['second'] == play['SECOND']) &
            (df2['down'] == play['DOWN']) &
            (df2['yds_to_go'] == play['TOGO']) &
            (df2['yardlinefixed'] == play['YARDLINEFIXED']) &
            ~(df2['detail'].str.startswith('Penalty')) &
            ~(df2['detail'].str.startswith('Timeout')) &
            (((df2['home_team'] == play['OFFENSETEAM']) & (df2['away_team'] == play['DEFENSETEAM'])) | ((df2['home_team'] == play['DEFENSETEAM']) & (df2['away_team'] == play['OFFENSETEAM'])))
        ]
    if len(matching_play.index) == 1:
        matching_play = matching_play.iloc[0]
        df1.loc[play.name, 'ISTURF'] = matching_play['isturf']
        df1.loc[play.name, 'UNDERROOF'] = matching_play['under_roof']
        df1.loc[play.name, 'WEATHER'] = matching_play['Weather']
        df1.loc[play.name, 'HOMETEAM'] = matching_play['home_team']
        df1.loc[play.name, 'AWAYTEAM'] = matching_play['away_team']
        df1.loc[play.name, 'HOMESCORE'] = matching_play['pbp_score_hm']
        df1.loc[play.name, 'AWAYSCORE'] = matching_play['pbp_score_aw']

    if play.name%1000 == 0:
        print play.name, 'of', df1.shape[0]

def add_features(pbp, pbp_pfr):

    # add some empty columns to fill
    pbp['ISTURF'] = np.nan
    pbp['UNDERROOF'] = np.nan
    pbp['WEATHER'] = np.nan
    pbp['HOMETEAM'] = np.nan
    pbp['AWAYTEAM'] = np.nan
    pbp['HOMESCORE'] = np.nan
    pbp['AWAYSCORE'] = np.nan

    # reset the index so the iloc matches the loc
    pbp.reset_index(inplace=True)

    # for each play in our main dataframe, find the corresponding play in the
    # other and copy the values over
    pbp.apply(lambda x: join(x, pbp, pbp_pfr), axis=1)

    return pbp

def reclean(pbp):

    # drop all of the remaining rows without a score
    # (there were 4 due to misalignment of the two data sources and 329 due to
    # missing data in scraped data, which is only 0.2% of the data)
    pbp = pbp[pbp.HOMESCORE.notnull()]

    # break out the values from the weather
    pbp = pd.concat([pbp, pbp.WEATHER.apply(lambda x: pd.Series(parse_weather(x)))], axis=1)

    # convert HOMETEAM / AWAYTEAM to ISATHOME relative to offense
    pbp['ISATHOME'] = pbp.apply(lambda x: 1 if x.OFFENSETEAM == x.HOMETEAM else 0, axis=1)

    # convert HOMESCORE / AWAYSCORE to scoring margin relative to offense
    pbp['SCORINGMARGIN'] = pbp.apply(lambda x: compute_margin(x), axis=1)

    return pbp

if __name__ == '__main__':

    # read in the cleaned NFL Savant data and combine it
    filenames = ['../data/pbp2016-clean.csv',
        '../data/pbp2015-clean.csv',
        '../data/pbp2014-clean.csv',
        '../data/pbp2013-clean.csv']
    pbp = combine(filenames)

    # read in the cleaned pro-football-reference data and combine it. do some
    # additional cleanup to get the data; we want the dataframe to look
    # user-friendly for presentation on the UI.  dummy variables and other
    # transformations should go in the modeling.py module.
    pbp_pfr = pd.read_csv('../data/pbp-pfr.csv')
    pbp = add_features(pbp, pbp_pfr) # this takes ~5 hours right now
    pbp = reclean(pbp)

    # split the data into a training and validation set (for the users and model to compete over)
    # 10% is about 13.5k plays
    pbp_train, pbp_validation = train_test_split(pbp, test_size = 0.1, random_state=22)

    # save the files
    pbp_train.to_csv('../data/pbp-training.csv', index=False)
    pbp_validation.to_csv('../data/pbp-validation.csv', index=False)
