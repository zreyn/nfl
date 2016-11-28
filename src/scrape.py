import pandas as pd
import numpy as np
import copy
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import os

'''
This script goes out and scrapes a second site for additional features.  High
level plan:
1) pull together a list of game links
2) go to each URL pull the full play-by-play table
3) Descriptions don't match, but clock/down/yards seem to match.  Pull the
pbp_score_aw and pbp_score_hm fields and attach them

However...
This turned out to be a huge pain in the ass. The responses from requesting the
URLs of the boxscore pages doesn't have all of the data. A bunch of the content
is loaded dynamically. So, we will have to simulate a browser and introduce a
long sleep to let it load dynamically. Of course, most of the time the load
doesn't completely.  Also, the Chrome browser driver is pretty flaky, so it
might be necessary to run the loop for getting complete pages a few times to
make sure we get everything. Ugh.

The pages loaded when we read the html locally. So:
1) Grab each of the partial pages from mongo and save them as a local file
2) Load that file in a browser, let it pull in some of the dynamic content, and
then save that complete content in mongo.
3) Wait a long-ass time (~3 hours without threading).
4) Pull the complete pages and scrape the data we need from it.

This would probably be best with Ghost driver and loadImages=False, but I'm
only doing this process once and can afford to let it run overnight.
'''

def get_complete_page(page_part):

    # prepare to transfer the key,value pairs to the new table
    season = page_part['season']
    week = page_part['week']
    gameid = page_part['gameid']
    url = page_part['url']
    html = page_part['html']

    # if we've already loaded this page, skip it
    if boxscore_pages.find_one({'url':url}) > 0:
        return

    # save the html to a file
    with open('boxscore.html', 'w') as f:
        f.write(html)
        f.close()

    # load that file in a browser to finish the dynamic loads.
    driver = webdriver.Chrome('/usr/local/share/chromedriver/chromedriver')
    driver.set_page_load_timeout(15)
    try:
        driver.get('file:///Users/zgreyn/Google%20Drive/galvanize/projects/nfl/notebooks/boxscore.html')
    except TimeoutException as ex:
        # bail out for now and come back later
        return

    # give it some time to load
    time.sleep(5)
    content = driver.page_source.encode('utf-8').strip()

    # store the html in MongoDB
    boxscore_pages.insert_one({'season':season, 'week':week, 'gameid':gameid, 'url': url, 'html':content})

    # quit the driver
    driver.quit()

    return

def parse_play_by_play(season, week, gameid, html):

    # create the soup
    soup = BeautifulSoup(html, 'html.parser')

    # find the game info table
    game_info_table = soup.find(id='game_info')

    # if this game hasn't been played yet, bail out
    if game_info_table is None:
        return

    # create a dictionary of game info
    game_info = {}
    game_info['season'] = season
    game_info['week'] = week
    game_info['game_id'] = gameid

    # get the other game-level info
    rows = game_info_table.findAll('tr')
    for tr in rows:
        key = tr.find('th')
        value = tr.find('td')

        # ignore the header row (doesn't have a key)
        if key is not None and value is not None:
            game_info[str(key.text)] = str(value.text)

    # find the play-by-play table
    pbp_table = soup.find(id='div_pbp')

    # get the home and away teams
    for x in pbp_table.find('thead').findAll('th'):
        stat = x.get('data-stat')
        if stat == 'pbp_score_aw':
            game_info['away_team'] = x.text
        if stat == 'pbp_score_hm':
            game_info['home_team'] = x.text

    # get the plays
    plays = []
    for x in pbp_table.find('tbody').findAll('tr'):

        # copy all of the game info in
        play = copy.deepcopy(game_info)

        # put all of the play info in
        cols = x.findAll(['th','td'])
        for col in cols:
            play[col.get('data-stat')] = col.text

        # skip header rows, which only have one cell
        if len(cols) > 1:
            plays.append(play)

    return plays

def clean(pbp_pfr):
    # drop columns we won't use
    pbp_pfr.drop(
        [
            'Over/Under',
            'Vegas Line',
            'Won Toss',
            'exp_pts_after',
            'exp_pts_before',
            'home_wp'
        ],
          axis=1, inplace=True,  errors='ignore')

    # drop all records not in a real quarter and map OT to 5
    quarters = ['1', '2', '3', '4', 'OT']
    pbp_pfr = pbp_pfr[(pbp_pfr['quarter'].isin(quarters))]
    pbp_pfr['quarter'] = pbp_pfr['quarter'].map({'1':'1', '2':'2','3':'3','4':'4','OT':'5'})

    # drop any plays without a time and split the time remaining in to minutes and seconds
    pbp_pfr = pbp_pfr[(pbp_pfr['qtr_time_remain'].notnull())]
    pbp_pfr['minute'] = map(lambda x: str(x).split(':')[0], pbp_pfr['qtr_time_remain'])
    pbp_pfr['second'] = map(lambda x: str(x).split(':')[1], pbp_pfr['qtr_time_remain'])
    pbp_pfr.drop(['qtr_time_remain'], axis=1, inplace=True,  errors='ignore')

    # the 50 yardline doesn't have a team, so give it one to smooth out parsing
    pbp_pfr = pbp_pfr[(pbp_pfr['location'].notnull())]
    pbp_pfr['location'].replace(' 50', 'THE 50', inplace=True)
    pbp_pfr['yardlinefixed'] = map(lambda x: str(x).split()[1], pbp_pfr['location'])

    # map the roof to under_roof boolean and drop the original column
    roof_to_boolean = {
            'outdoors': 0,
            'dome' : 1,
            'retractable roof (open)' : 0,
            'retractable roof (closed)' : 1
        }
    pbp_pfr['under_roof'] = pbp_pfr['Roof'].map(roof_to_boolean)
    pbp_pfr.drop(['Roof'], axis=1, inplace=True,  errors='ignore')

    # map the surface to grass/turf
    surface_map = {
            'grass ' : 'grass',
            'fieldturf ' : 'turf',
            'fieldturf' : 'turf',
            'sportturf' : 'turf',
            'astroplay' : 'turf',
            'a_turf' : 'turf',
            'matrixturf' : 'turf',
            'grass' : 'grass'
        }
    pbp_pfr['isturf'] = pbp_pfr['Surface'].map(surface_to_isturf)
    pbp_pfr.drop(['Surface'], axis=1, inplace=True,  errors='ignore')

    # There are 238 games (~26%) without weather data; we should replace them with 'UNKNOWN'
    pbp_pfr['Weather'] = pbp_pfr['Weather'].fillna('UNKNOWN')

    # some details are just missing, others are timeouts and other such plays; replace with 'UNKNOWN'.
    pbp_pfr['detail'] = pbp_pfr['detail'].fillna('UNKNOWN')

    # almost all of the plays missing 'down' are kick-offs, 2-pt conversions, and penaltys; drop them
    pbp_pfr = pbp_pfr[(pbp_pfr['down'].notnull())]

    # the two data sources use different naming conventions, so adapt to one
    team_name_map =  {
            'BAL' : 'BAL',
            'CIN' : 'CIN',
            'MIN' : 'MIN',
            'MIA' : 'MIA',
            'TAM' : 'TB',
            'ATL' : 'ATL',
            'KAN' : 'KC',
            'SEA' : 'SEA',
            'GNB' : 'GB',
            'HOU' : 'HOU',
            'NYJ' : 'NYJ',
            'SDG' : 'SD',
            'STL' : 'LA',
            'JAX' : 'JAX',
            'SFO' : 'SF',
            'PIT' : 'PIT',
            'ARI' : 'ARI',
            'NYG' : 'NYG',
            'DET' : 'DET',
            'CLE' : 'CLE',
            'BUF' : 'BUF',
            'IND' : 'IND',
            'CHI' : 'CHI',
            'OAK' : 'OAK',
            'DAL' : 'DAL',
            'PHI' : 'PHI',
            'WAS' : 'WAS',
            'NOR' : 'NO',
            'NWE' : 'NE',
            'CAR' : 'CAR',
            'DEN' : 'DEN',
            'TEN' : 'TEN',
            'LAR' : 'LA'
        }
    pbp_pfr['away_team'] = pbp_pfr['away_team'].map(team_name_map)
    pbp_pfr['home_team'] = pbp_pfr['home_team'].map(team_name_map)

    # change the types of a few columns
    pbp_pfr['down'] = pbp_pfr['down'].astype("int64")
    pbp_pfr['pbp_score_aw'] = pbp_pfr['pbp_score_aw'].astype("int64")
    pbp_pfr['pbp_score_hm'] = pbp_pfr['pbp_score_hm'].astype("int64")
    pbp_pfr['quarter'] = pbp_pfr['quarter'].astype("int64")
    pbp_pfr['yds_to_go'] = pbp_pfr['yds_to_go'].astype("int64")
    pbp_pfr['minute'] = pbp_pfr['minute'].astype("int64")
    pbp_pfr['second'] = pbp_pfr['second'].astype("int64")
    pbp_pfr['yardlinefixed'] = pbp_pfr['yardlinefixed'].astype("int64")

    return pbp_pfr

def main(output_filename):

    # connect to the hosted MongoDB instance
    client = MongoClient('mongodb://localhost:27017/')

    # open the nfl db
    db = client['nfl']
    week_pages = db['week_pages']
    boxscore_pages_partial = db['boxscore_pages_partial']
    boxscore_pages = db['boxscore_pages']

    # for each season and each week
    seasons = ['2013', '2014', '2015', '2016']
    for season in seasons:
        for week in xrange(1,18):

            # construct the url for the game's box score and request it
            url = 'http://www.pro-football-reference.com/years/'+season+'/week_'+str(week)+'.htm'
            r = requests.get(url)

            # store the html in MongoDB
            week_pages.insert_one({'season':season, 'week':week, 'url': url, 'html':r.content})

    url_prefix = 'http://www.pro-football-reference.com'
    boxscore_urls = {}

    # extract the game boxscore links
    for page in week_pages.find():
        html = page['html']

        # have BeautifulSoup crack it open
        soup = BeautifulSoup(html, 'html.parser')

        # find the game boxscore links
        for game_link in soup.select('td.gamelink'):
            for link in game_link.find_all('a'):
                boxscore_urls[url_prefix+link.get('href')] = {'week': page['week'], 'season':page['season']}

    # scrape the boxscore pages
    for i,url in enumerate(boxscore_urls.keys()):

        # show the status
        print i+1, 'of', len(boxscore_urls), url

        # get the meta data
        week = boxscore_urls[url]['week']
        season = boxscore_urls[url]['season']

        # extract the gameid
        gameid = url.rsplit('/', 1)[-1][:-4]

        # request the page
        r = requests.get(url)

        # store the html in MongoDB
        boxscore_pages_partial.insert_one({'season':season, 'week':week, 'gameid':gameid, 'url': url, 'html':r.content})

    # go get the rest of the pages - this is the loop that may need to run a few times
    total = boxscore_pages_partial.count()
    for i,page_part in enumerate(boxscore_pages_partial.find()):

        print i+1, 'of', total
        get_complete_page(page_part)


    # Grab the html from mongo and parse the stuff we need, then pack it into a mega dataframe
    i = 0
    total = boxscore_pages.count()
    pbp_dfs = []
    for page in boxscore_pages.find():

        # show progress
        i += 1
        print i, 'of', total

        # scrape the plays as a list of dictionaries, with game-level info included
        if 'html' in page.keys():
            plays = parse_play_by_play(page['season'], page['week'], page['gameid'], page['html'])

        # make sure we got some data
        if plays is not None:

            # create a dataframe from the plays
            plays_df = pd.DataFrame.from_dict(plays)

            # put it on the list of dataframe
            pbp_dfs.append(plays_df)

    # combine all the play-by-play data into one
    pbp_pfr = pd.concat(pbp_dfs)

    # clean the data a bit
    pbp_pfr = clean(pbp_pfr)

    # output the compiled data frame to save it
    pbp_pfr.to_csv(output_filename, index=False)

if __name__ == '__main__':
    main(os.path.join(os.path.dirname(__file__),'../data/pbp-pfr.csv'))
