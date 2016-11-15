# Predicting the Play in the NFL

Author: Zane Reynolds (@zreyn)
Date: November 2016

### The Problem

From the perspective of an NFL Defensive Coordinator, having an instant data-driven prediction of what play the opposing offense will run is extremely valuable.  Knowing what play is coming can influence which defensive personnel to have on the field and in which coverage.   Most of the prior art in this domain is dedicated to predicting the outcomes of games instead of individual plays.


### Data

I gathered NFL play data over the course of the 2013-2016 seasons from NFL Savant:
http://nflsavant.com/about.php

Since the play data is not specific to this purpose, it includes many columns and rows that are extraneous.  Scripts to clean and transform the data are included in the src directory.

Ultimately, I produced a data set includes the following features:
* Quarter
* Minute
* Second
* OffenseTeam
* Down
* ToGo
* YardLine
* Formation
* Play

The 'Play' column is the target value consisting of 3 labels: {RUN, PASS, KICK}

The data contains a total of 134,998 offensive plays run from 2013 - Wk 10 2016.

### Modeling

Given situational features like the time on the game clock, the down, and yards to go, I built modles to predict the result of the play.  Initially, I evaluated several general models (not specific to season or team offense) including a Random Forest and Gradient Boosting Classifier.  


While there are hundreds of thousands of plays executed during each NFL season, the amount of data per offense and situation is limited, so the data's density is low.  In addition, the players and play callers for offenses change year over year and even week to week, making historical data less pertinent to predicting upcoming plays.



### Evaluation

We can evaluate the performance of the models in two ways. 1) Split off a validation set of randomly selected plays throughout the data set.  Cross-validation and tuning will be performed on the training set and the generalization measured on the validation set.  2) Use previous seasons data as the training set and evaluate on plays run in the current season.  Ultimately, we want to know how it will perform "live" during games. NFL offenses typical pass 57% of the time, so the model must show at least a 10% improvement to be effective.


### Deployment

The user interface presents the user with a situation as if they are a defense (clock, team, yard line, formation); they will choose what to defend (short/long pass, run, kick, etc.).  The model will also make a prediction, but that is shown to the user after they have made their own prediction. The ground truth will be displayed and both predictions evaluated.  Compete against the model!
