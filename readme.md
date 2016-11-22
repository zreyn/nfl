# Predicting the Play in the NFL

Author: Zane Reynolds (@zreyn)
Date: November 2016

### The Problem

From the perspective of an NFL Defensive Coordinator, having an instant data-driven prediction of what play the opposing offense will run is extremely valuable.  Knowing what play is coming can influence which defensive personnel to have on the field and in which coverage.   Most of the prior art in this domain is dedicated to predicting the outcomes of games instead of individual plays.


### Data

I gathered NFL play data over the course of the 2013-2016 seasons from NFLSavant.com and from Pro-Football-Reference.com.

Since the play data is not specific to predicting offensive plays, it includes many extraneous columns and rows.  For example, the data includes plays that never began due to timeouts or penalties such as false starts, encroachment, or delay of game.  So, I created scripts to clean and transform the data, which can be found in the src directory.

Ultimately, I produced a data set includes the following features (data source in parentheses):
* GAMEID            - (NFLSavant) A unique identifier for each game
* GAMEDATE          - (NFLSavant) The date the game took place in YYYY-MM-DD format
* QUARTER           - (NFLSavant) The quarter in which the play took place
* MINUTE            - (NFLSavant) The minutes on the clock when the play took place
* SECOND            - (NFLSavant) The seconds on the clock when the play took place
* OFFENSETEAM       - (NFLSavant) The three-letter team code of which team was on offense for the play
* DEFENSETEAM       - (NFLSavant) The three-letter team code of which team was on defense for the play
* DOWN              - (NFLSavant) The down
* TOGO              - (NFLSavant) The number of yards to go for a first down or touchdown
* YARDLINE          - (NFLSavant) The absolute ball position where the play took place (i.e. own 45 = 45, opp 45 = 55)
* DESCRIPTION       - (NFLSavant) The text description of what happened during the play
* SEASONYEAR        - (NFLSavant) Which season year the play took place (January 2014 games belong to season 2013)
* YARDS             - (NFLSavant) The yards gained on the play
* FORMATION         - (NFLSavant) Where the quarterback lined up during the play
* PLAYTYPE          - (NFLSavant) The outcome of the play
* PASSTYPE          - (NFLSavant) The length and direction of the pass attempt
* RUSHDIRECTION     - (NFLSavant) The direction of the run in terms of the offensive line (right guard, left tackle)
* YARDLINEFIXED     - (NFLSavant) The relative ball position on the field (0-50)
* YARDLINEDIRECTION - (NFLSavant) The relative side of the field (own, opp)
* UNDERROOF         - (Pro-Football-Reference) Whether the game was played under a dome or closed retractable roof
* WEATHER           - (Pro-Football-Reference) The weather on the field at game time
* HOMETEAM          - (Pro-Football-Reference) Which team was the home team
* AWAYTEAM          - (Pro-Football-Reference) Which team was the away team
* HOMESCORE         - (Pro-Football-Reference) The home team's score at the time of the play
* AWAYSCORE         - (Pro-Football-Reference) The away team's score at the time of the play
* ISTURF            - (computed) From Pro-Football-Reference's Surface attribute, simplified to artificial or not
* HUMIDITY          - (computed) The relative humidity parsed from the Weather
* TEMPERATURE       - (computed) The temperature in degrees Farenheit parsed from the Weather
* WINDSPEED         - (computed) The wind speed parsed from the Weather
* ISATHOME          - (computed) Whether the offense was at home for the play
* SCORINGMARGIN     - (computed) The score difference relative to the offense at the time of the play
* PLAY              - (computed) CLASSIFICATION TARGET: The outcome of the play (RUSH, PASS, KICK)

Merging the two data sources revealed 4 plays where the data from Pro-Football-Reference was erroneous, so those plays were discarded.  Additionally, several games (totaling 333 plays) were not properly scraped from Pro-Football-Reference, so they were also discarded from the final data.  It's possible a rescraping could recover these plays.

The final cleaned data contains a total of 121,525 offensive plays run from 2013 - Wk 10 2016 and has 33 features.  This data was split into a training and validation set containing 109,372 and 12,153 plays respectively.

To reproduce the data:
1. Download NFL Savant data (http://nflsavant.com/about.php) and run src/clean.py
2. Scrape Pro-Football-Reference (http://www.pro-football-reference.com/) using src/scrape.py
3. Combine the two data sources and create a training and a validation set using src/combine.py
4. The result is two .csv files: pbp-training and pbp-validation.

### Modeling

The cleaned data is in human-friendly form, which includes categorical features such as the teams and formation, some redundant columns, and missing values.  However, scikitlearn's classifiers require additional data preparation to ensure all values are present and numeric.  Categorical variables were dummied, redundant columns dropped, and missing values filled (see src/modeling.py).

The features available to the models are:

* QUARTER                     - int64
* MINUTE                      - int64
* SECOND                      - int64
* DOWN                        - int64
* TOGO                        - int64
* YARDLINE                    - int64
* SCORINGMARGIN               - float64
* ISTURF                      - float64
* UNDERROOF                   - float64
* ISATHOME                    - int64
* TEMPERATURE                 - int64
* HUMIDITY                    - int64
* WINDSPEED                   - int64
* SEASONYEAR                  - int64
* PLAY                        - int64
* TEAM_ARI                    - uint8
* TEAM_ATL                    - uint8
* TEAM_BAL                    - uint8
* TEAM_BUF                    - uint8
* TEAM_CAR                    - uint8
* TEAM_CHI                    - uint8
* TEAM_CIN                    - uint8
* TEAM_CLE                    - uint8
* TEAM_DAL                    - uint8
* TEAM_DEN                    - uint8
* TEAM_DET                    - uint8
* TEAM_GB                     - uint8
* TEAM_HOU                    - uint8
* TEAM_IND                    - uint8
* TEAM_JAX                    - uint8
* TEAM_KC                     - uint8
* TEAM_LA                     - uint8
* TEAM_MIA                    - uint8
* TEAM_MIN                    - uint8
* TEAM_NE                     - uint8
* TEAM_NO                     - uint8
* TEAM_NYG                    - uint8
* TEAM_NYJ                    - uint8
* TEAM_OAK                    - uint8
* TEAM_PHI                    - uint8
* TEAM_PIT                    - uint8
* TEAM_SD                     - uint8
* TEAM_SEA                    - uint8
* TEAM_SF                     - uint8
* TEAM_TB                     - uint8
* TEAM_TEN                    - uint8
* TEAM_WAS                    - uint8
* FORMATION_FIELD_GOAL        - int64
* FORMATION_NO_HUDDLE         - int64
* FORMATION_NO_HUDDLE_SHOTGUN - int64
* FORMATION_PUNT              - uint8
* FORMATION_SHOTGUN           - uint8
* FORMATION_UNDER_CENTER      - int64
* FORMATION_WILDCAT           - uint8

Given these features, I built models to predict the result of the play.  To select a model, I evaluated a number of classifiers:
* Nearest Neighbors : (0.61435390946502055, 0.61175918336192536, 0.61435390946502055)
* Linear SVM : (0.75845267489711932, 0.76109746949409385, 0.75845267489711932)
* Decision Tree : (0.76111934156378602, 0.76084891169251845, 0.76111934156378602)
* Random Forest : (0.63940740740740742, 0.6744484222482392, 0.63940740740740742)
* Neural Net : (0.75545679012345679, 0.76463056672255336, 0.75545679012345679)
* AdaBoost : (0.73527572016460907, 0.73277847768683679, 0.73527572016460907)
* Naive Bayes : (0.69659259259259254, 0.69878651384999224, 0.69659259259259254)
* QDA : (0.64483950617283947, 0.77238414772099007, 0.64483950617283947) (WARN: Variables are collinear)
* Gradient Boosting : (0.76628806584362141, 0.76617421290936849, 0.76628806584362141)
* Logistic Regression : (0.75621399176954729, 0.75502222772245453, 0.75621399176954729)

Based on the results, I selected the GradientBoostingClassifier, which was consistently the most accurate.

While there are hundreds of thousands of plays executed during each NFL season, the amount of data per offense and situation is limited, so the data's density is low.  In addition, the players and play callers for offenses change year over year and even week to week, making historical data less pertinent to predicting upcoming plays.  As such, I conducted a number of feature engineering experiments such as:

* Including vs excluding offense team, defense team, season
* Including vs excluding score, weather, formation
* Stacking a "general wisdom" (not year or offense specific) model, which provided log-odds of RUSH, PASS, KICK as features to the final model

However, each of the variations produced results within about 1% accuracy of the basic GradientBoostingClassifier.  To create the final model, I performed a grid search

* learning_rate: [0.1, 0.01]
* min_samples_leaf: [5, 20, 200]
* max_features: [1.0, 0.5, 0.1]
* n_estimators: [500, 100]
* random_state: [22]

To build the selected model:
1. Use src/modeling.py to prep the data (convert categorical variables to dummies) and fit the model.

To use the final model I built:
1. Unpickle data/gbc-v6.pkl


### Evaluation

Beyond the cross-validation scores and accuracy on the validation set, the quality of the model will be evaluated based on its performance against two competing models: 1) NFL offenses typical pass 57% of the time, so a naive model always guessing pass will be right 57% of the time.  2) Humans, given the same information.

While I have no NFL Defensive Coordinators on hand to compete against the model, I had several Monday morning quarterbacks compete aginst the model.  Human accuracy tends to hover around the 65-70% range while the model accuracy tends to converge on 76%.  


### Deployment

I created a user inteface that loads the validation set, held out from training and tuning.  It presents the user with a randomly selected play from that validation set.  The user is presented with the situation as if they are a defense (the cleaned features); they choose whether to defend the pass, the rush, or a kick.  The model will also make a prediction, but that is only shown to the user after they have made their own prediction. The ground truth will be displayed and both predictions evaluated.  The user's individual performance against the model is tracked via browser cookie and the aggregated user performance is tracked and displayed as confusion matrices.

The final UI was uploaded to an EC2 instance to serve traffic.

To run:
1. Make sure you've produced the clean data and built the model.
2. Run src/app.py
