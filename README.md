# 2019 NFL Big Data Bowl Submission
#### by Sam Setegne

## Table of Contents
[Introduction](#introduction)
##### Using The Catch Separation Tool
[Functional Flow of Catch Separation Model API](#functional-flow-of-catch-separation-model-api)  
[Making a Catch Separation Prediction Using Pre-Snap Information](#making-a-catch-separation-prediction-using-pre-snap-information)  
[View Animations Created From Player Tracking Data](#view-animations-created-from-player-tracking-data)  
##### Model Development
[Importing the tracking data into pandas](#importing-the-tracking-data-into-pandas)  
[Identifying Who Caught the Football & the Closest Defender](#identifying-who-caught-the-football--the-closest-defender)  
[Calculating Catch Separation](#calculating-catch-separation)  
[Identifying The Type of Receiver-Routes](#identifying-the-type-of-receiver-routes)  
[Add Additional Features from Raw Play Data](#add-additional-features-from-raw-play-data)  
[Preparing the Data for Training: One Hot Encoding](#preparing-the-data-for-training-one-hot-encoding)  
[Preparing Data & Training KNN Model](#preparing-data--training-knn-model)  
[Preparing the Data for Training: Train-Test Split](#preparing-the-data-for-training-train-test-split)  
[Training the K-Nearest-Neighbor Regression Model](#training-the-k-nearest-neighbor-regression-model)  

# Introduction

By now, everyone has read one of the many articles detailing how Big Data and data science have lead to influential changes in how the sports world approaches analytics. From player tracking to pattern recognition to interactions between fans on social media, massive amounts of data (a.k.a potential) is being collected daily. Even though we're not even close to pushing the limits, data science has already made remarkable impacts in player safety, league competitiveness, fan engagement, and advertising.  In my submission to the ![2019 NFL Big Data Bowl competition](https://github.com/nfl-football-ops/Big-Data-Bowl), I've chosen to tackle theme number 3, identifying the best receiver-route combinations.

In this guide, I will walk you through the development and implementation of a real-time API that uses a K-Nearest-Neighbor regression model to make a pre-snap prediction of how much separation the target receiver will have from the closest defender. To see the final product, head over to http://nfl.mercutioanalytics.com/ and while you're there, check out the graphic visualizations for every play of every game!

# Using The Catch Separation Tool

## Functional Flow of Catch Separation Model API
![](http://yuml.me/diagram/plain;dir:lr;scale:150/class/[Analyst{bg:tan}]->[Pre-snap%20Information{bg:springgreen}],[Pre-snap%20Information]->[Catch%20Separation%20API{bg:tomato}],[Catch%20Separation%20API]->[Scoring%20Engine{bg:red}],[Scoring%20Engine]->[Predicted%20Catch%20Separation{bg:gold}],[Predicted%20Catch%20Separation]->[Catch%20Separation%20API],[Catch%20Separation%20API]->[Analyst] "yUML")

## Making a Catch Separation Prediction Using Pre-Snap Information

To make a pre-snap catch separation prediction, head over to http://nfl.mercutioanalytics.com/ and click on **Catch Separation Prediction Tool**.

![Home MaaS](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/home_maas.png)

Complete the Pre-Snap Information Form, including the routes for each receiver (Enter the route for the primary target in the **Target's Route** field.)

![CSM Input Screen](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/csm_input_screen.png)

Click **Predict Catch Separation!** and the Pre-Snap information will be processed through the Catch Separation Model and a predicted catch separation value in yards between the receiver and the closest defending corner will be displayed.

![Prediction Screen](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/prediction_screen.png)

## View Animations Created From Player Tracking Data

To view animations of the tracking data, head to http://nfl.mercutioanalytics.com/ and click **Visualize Tracking Data**.

![Home Visualize](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/home_visualize.png)

From the list of games, select a game that you wish to view.

![Games](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/games.png)

After you select a game, you will see a list of descriptions for each play from that game. Select the play that you wish to view.

![Plays](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/plays.png)

The field will be displayed with the players on the home team shown as red circles, and the plays on the away team shown as blue circles. Each WR, TE, RB, and FB on the offense is highlighted with a circle that has a 5 yard radius. You can start the animation by clicking **Play** and pause the animation by clicking **Pause**.

![Animation](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/animation.png)

# Model Development

## Importing the tracking data into pandas

Since we'll be doing a good number of manipulations to the data, here's a handy flow-chart the summarizes this section.
![](http://yuml.me/diagram/plain;dir:lr;scale:80/class/[Tracking%20Data{bg:seagreen}]->[Identify%20Catch%20Receiver%20&%20Closest%20Corner],[Identify%20Catch%20Receiver%20&%20Closest%20Corner]->[Calculate%20Catch%20Separation%20(Distance%20between%20receiver%20and%20closest%20defender%20at%20catch%20frame)],[Calculate%20Catch%20Separation%20(Distance%20between%20receiver%20and%20closest%20defender%20at%20catch%20frame)]->[Identify%20Routes%20of%20Each%20Receiver|X-Route%20options:;Short;Medium;Deep|Y-Route%20Options:;Stop;Slant;Flat;Out;In;Post;Corner;Fly],[Identify%20Routes%20of%20Each%20Receiver|X-Route%20options:;Short;Medium;Deep|Y-Route%20Options:;Stop;Slant;Flat;Out;In;Post;Corner;Fly]->[Create%20a%20Main%20Modeling%20Dataset],[Play%20Data]-.->[Create%20a%20Main%20Modeling%20Dataset],[Create%20a%20Main%20Modeling%20Dataset]->[Prepare%20Data|Features:;Target's%20X-Route;Target's%20Y-Route;2nd%20Receiver's%20X-Route;2nd%20Receiver's%20Y-Route;3rd%20Receiver's%20X-Route;3rd%20Receiver's%20Y-Route;4th%20Receiver's%20X-Route;4th%20Receiver's%20Y-Route;Down;Yards-To-Go;Offense%20Formation;Defenders%20in%20The%20Box;Pass%20Rushers;Offense%20Personnel;Defense%20Personnel|Label:;Catch%20Separation%20(yds){bg:steelblue}] "yUML")

To optimize the performance of handling the raw data, we'll load the csv file for each game into a pandas DataFrame, and place them all into a lookup dictionary that we'll serialize and store as a pickle file.

```py
import pandas as pd
import pickle as p

# Cache data for all games in a dictionary to optimize subsequent code
dfgames = pd.read_csv(r'Data/games.csv')
games = {}
for gameId in dfgames['gameId']:
	games[gameId] = pd.read_csv(r'Data/tracking_gameId_' + str(gameId) + '.csv')
	print("Data for game " + str(gameId) + " saved...")
	
p.dump(games, open(r'derivedData/games.pkl','wb'))
```

Now we can quickly load in data from all of the games by simply unpickling 'games.pkl'.

## Identifying Who Caught the Football & the Closest Defender

We'll turn this process into a function that we can use repeatedly, but for now let's just pull out some data on a completed pass play to use. Let's use play 3387 in game 2017091008, a deep pass to Zach Ertz from Carson Wentz for a 23 yard gain.

```py
# Load the data for all games
games = p.load(open(r'derivedData/games.pkl', 'rb'))
# Filter to game 2017091008
dfgame = games[2017091008]
# Filter to the specific frame in play 3387 when the ball is caught
dfcatch = dfgame[(dfgame['playId'] == 3387) & (dfgame['event'] == 'pass_outcome_caught')]
```

Now create a separate tuple containing the footballs x and y coordinates and filter our catch dataset to only contain the tracking data for the players.
```py
ball_point = (dfcatch[(dfcatch['team']=='ball')]['x'].values[0], dfcatch[(dfcatch['team']=='ball')]['y'].values[0])
dfcatch_players = dfcatch[(dfcatch['team'] != 'ball')]
```

We can identify who caught the ball by comparing the coordinates of the ball to the coordinates of the rest of the players. Let's import some tools and create a function at the top of our code to do just that.

```py
from scipy.spatial import distance

# Function to find the closest point from an array of points
def closest_node(center_point, surrounding_points):
    '''
    center_point: Pass in a point as a tuple of (x, y)
    surrounding_points: Pass in points as an array of (x, y) points to compare
    Function will return the point within the surrounding_points array that's closest to center_point
    '''
    closest_index = distance.cdist([center_point], surrounding_points).argmin()
    return surrounding_points[closest_index]
```

Next, convert the players points to an array and use the function above to find the closest player to the ball when it was caught (The receiver who caught the ball)
```py
player_points = dfcatch_players[['x','y']].values
closest_player_coordinates = closest_node(ball_point, player_points)
catch_player = dfcatch[(dfcatch['x'] == closest_player_coordinates[0]) & (dfcatch['y'] == closest_player_coordinates[1])]
# Find the team of the player who caught the ball
team = catch_player['team'].values[0]
```

Use the same technique to find the closest defender to the receiver who caught the ball.
```py
# Filter the catch data to only the players on the opposite team
if team == 'home':
	dfcatch_corners = dfcatch[(dfcatch['team'] != 'ball') & (dfcatch['team'] == 'away')]
elif team == 'away':
	dfcatch_corners = dfcatch[(dfcatch['team'] != 'ball') & (dfcatch['team'] == 'home')]
else:
	raise ValueError("Receiving players team unable to be identified.")

# Convert the receivers coordinates into a tuple
receiver = tuple(closest_player_coordinates)

# Convert the corners points to an array
corners_points = dfcatch_corners[['x','y']].values

# Calculate the coordinates of the closest corner to the receiver
closest_corner_coordinates = closest_node(receiver, corners_points)

# Filter the catch frame data to those coordinates to identify the closest corner to the receiver who caught the ball
defending_corner = dfcatch[(dfcatch['x'] == closest_corner_coordinates[0]) & (dfcatch['y'] == closest_corner_coordinates[1])]
```

## Calculating Catch Separation

Let's ``` import math ``` and create another simple function that we can use to calculate the distances between the players (the catch separation).
```py
import math

# Function to calculate the distance between two points
def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist
```

All we have to do now is calculate the catch separation and add that value (along with who caught the ball and who the closest defender was) to our data.
```py
# Calculate the distance between the receiver and the corner (or closest player on the other team)
# Distance object type is float and the units are yards
corner_distance = calculateDistance(catch_player['x'].values[0], catch_player['y'].values[0], defending_corner['x'].values[0], defending_corner['y'].values[0])

# Create a copy of dfcatch
dfcatch_wSeparation = dfcatch

# Add the distance of the closest player to the receiver to a field called catchSeparation
dfcatch_wSeparation['catchSeparation'] = corner_distance
dfcatch_wSeparation['catchingReceiver'] = catch_player['displayName'].values[0]
dfcatch_wSeparation['closestCorner'] = defending_corner['displayName'].values[0]
```

Since we'll be doing this for every completed pass contained in the data, let's put all of this in a nice compact function.
```py
def addCatchSeparation(dfcatch):
    ball_point = (dfcatch[(dfcatch['team']=='ball')]['x'].values[0], dfcatch[(dfcatch['team']=='ball')]['y'].values[0])
	
    dfcatch_players = dfcatch[(dfcatch['team'] != 'ball')]
    player_points = dfcatch_players[['x','y']].values
    closest_player_coordinates = closest_node(ball_point, player_points)
    catch_player = dfcatch[(dfcatch['x'] == closest_player_coordinates[0]) & (dfcatch['y'] == closest_player_coordinates[1])]
	
    team = catch_player['team'].values[0]

    if team == 'home':
        dfcatch_corners = dfcatch[(dfcatch['team'] != 'ball') & (dfcatch['team'] == 'away')]
    elif team == 'away':
        dfcatch_corners = dfcatch[(dfcatch['team'] != 'ball') & (dfcatch['team'] == 'home')]
    else:
        raise ValueError("Receiving players team unable to be identified.")

    receiver = tuple(closest_player_coordinates)
    corners_points = dfcatch_corners[['x','y']].values
    closest_corner_coordinates = closest_node(receiver, corners_points)
    defending_corner = dfcatch[(dfcatch['x'] == closest_corner_coordinates[0]) & (dfcatch['y'] == closest_corner_coordinates[1])]
	
    corner_distance = calculateDistance(catch_player['x'].values[0], catch_player['y'].values[0], defending_corner['x'].values[0], defending_corner['y'].values[0])
	
    dfcatch_wSeparation = dfcatch
    dfcatch_wSeparation['catchSeparation'] = corner_distance
    dfcatch_wSeparation['catchingReceiver'] = catch_player['displayName'].values[0]
    dfcatch_wSeparation['closestCorner'] = defending_corner['displayName'].values[0]
    
    
    return dfcatch_wSeparation
```

Now that we have a function we can pass in some catch data to and have the receiver, defender, and catch separation added, let's loop through every game and do this for every play then combine this data into a DataFrame called ``` main_df ```. The ``` if ``` will execute for the first loop to create main_df with the plays from the first game, then every loop after will fall to ``` else ``` and will simply append the data to the already created DataFrame main_df.

```py
for main_counter, gameId in enumerate(games):
    if main_counter == 0:
        dfgame = games[gameId]
        for counter, play in enumerate(dfgame[(dfgame['event'] == 'pass_outcome_caught')]['playId'].unique()):
            if counter == 0:
                playdf = dfgame[(dfgame['playId'] == play)]
                catchFrame = playdf[(playdf['event'] == 'pass_outcome_caught')]['frame.id'].values[0]
                indf = playdf[(playdf['frame.id'] == catchFrame)]
                try:
                    newdf = addCatchSeparation(indf)
                except:
                    print("Failed to calculate catch separation for play " + str(play) + " in game " + str(gameId))
            else:
                playdf = dfgame[(dfgame['playId'] == play)]
                catchFrame = playdf[(playdf['event'] == 'pass_outcome_caught')]['frame.id'].values[0]
                indf = playdf[(playdf['frame.id'] == catchFrame)]
                try:
                    adddf = addCatchSeparation(indf)
                    newdf = pd.concat([newdf, adddf], ignore_index=True)
                except:
                    print("Failed to calculate catch separation for play " + str(play) + " in game " + str(gameId))

        # Create a dataframe that has a single row for each play with the fields 'gameId', 'playId', 'catchingReceiver', 'closestCorner', 'catchSeparation'
        df_distinctPlays = newdf[['gameId', 'playId', 'catchingReceiver', 'closestCorner', 'catchSeparation']].drop_duplicates()
        main_df = df_distinctPlays
    else:
        dfgame = games[gameId]
        for counter, play in enumerate(dfgame[(dfgame['event'] == 'pass_outcome_caught')]['playId'].unique()):
            if counter == 0:
                playdf = dfgame[(dfgame['playId'] == play)]
                catchFrame = playdf[(playdf['event'] == 'pass_outcome_caught')]['frame.id'].values[0]
                indf = playdf[(playdf['frame.id'] == catchFrame)]
                try:
                    newdf = addCatchSeparation(indf)
                except:
                    print("Failed to calculate catch separation for play " + str(play) + " in game " + str(gameId))
            else:
                playdf = dfgame[(dfgame['playId'] == play)]
                catchFrame = playdf[(playdf['event'] == 'pass_outcome_caught')]['frame.id'].values[0]
                indf = playdf[(playdf['frame.id'] == catchFrame)]
                try:
                    adddf = addCatchSeparation(indf)
                    newdf = pd.concat([newdf, adddf], ignore_index=True)
                except:
                    print("Failed to calculate catch separation for play " + str(play) + " in game " + str(gameId))

        # Create a dataframe that has a single row for each play with the fields 'gameId', 'playId', 'catchingReceiver', 'closestCorner', 'catchSeparation'
        df_distinctPlays = newdf[['gameId', 'playId', 'catchingReceiver', 'closestCorner', 'catchSeparation']].drop_duplicates()
        main_df = pd.concat([main_df, df_distinctPlays], ignore_index=True)
```

Two more columns are needed: One to identify which team is on offense, and a second to identify which team is on defense.
```py
# Add two columns to main_df that show which team is on offense or defense (teams are identified as 'home' or 'away')
gameId_check = 0
for index, row in main_df.iterrows():
	if row['gameId'] == gameId_check:
		pass
	else:
		dfgame = games[row['gameId']]
		gameId_check = row['gameId']
	main_df.loc[index,'offense'] = dfgame[(dfgame['displayName'] == row['catchingReceiver'])]['team'].values[0]
	main_df.loc[index,'defense'] = dfgame[(dfgame['displayName'] == row['closestCorner'])]['team'].values[0]
```

## Identifying The Type of Receiver-Routes

To identify the route of every receiver on the field, we're going to analyze how the coordinates of the player evolves from snap to when the ball is caught (either by them or a teammate) and we'll base our analysis on a basic route tree. (See this great article by Matt Bowen over at Bleacher Report on route tree basics: ![NFL 101: Breaking Down the Basics of the Route Tree](https://bleacherreport.com/articles/2016841-nfl-101-breaking-down-the-basics-of-the-route-tree))

In the first half of the code below, we categorize the x movement of the player as 'short', 'medium', or 'deep' by checking for 0-15yds, 15-30yds, and 30+ yards respectively. After that we categorize the y movement of the player as either 'out', 'in', or 'fly' by checking for movement cutting either towards the center of the field, away from the center of the field, or neither. Finally, we take a look at both the x and y routes and compare them to a basic route tree. For example, a 'short' 'out' route would convert to a 'flat' route and a 'deep' 'in' route would convert to a 'post' route.
```py
# Add receiverMates to main_df and their x and y routes as well as the x and y route for catchReceiver
for index, row in main_df.iterrows():
	df = games[row['gameId']]
	df_players = pd.read_csv(r'Data/players.csv')
	df_players = df_players[['nflId','PositionAbbr']]
	df = df.join(df_players.set_index('nflId'), on='nflId')
	dfplay = df[(df['playId'] == row['playId'])]
	receiverMateCounter = 0
	for displayName in dfplay[(dfplay['event'] == 'pass_outcome_caught') & (dfplay['team'] == row['offense']) & (dfplay['PositionAbbr'].isin(['TE','WR','RB','FB']))]['displayName'].unique():
		receiver = False
		if displayName == row['catchingReceiver']:
			receiver = True
		else:
			receiverMateCounter = receiverMateCounter + 1
		xdis = abs(dfplay[(dfplay['displayName'] == displayName) & (dfplay['frame.id'] == dfplay['frame.id'].min())]['x'].values[0] - dfplay[(dfplay['displayName'] == displayName) & (dfplay['event'] == 'pass_outcome_caught')]['x'].values[0])
		if xdis <= 15:
			xroute = 'short'
		elif xdis > 15 and xdis <= 30:
			xroute = 'medium'
		elif xdis > 30:
			xroute = 'deep'
		yi = dfplay[(dfplay['displayName'] == displayName) & (dfplay['frame.id'] == dfplay['frame.id'].min())]['y'].values[0]
		yf = dfplay[(dfplay['displayName'] == displayName) & (dfplay['event'] == 'pass_outcome_caught')]['y'].values[0]
		if yi <= 26.5:
			if yf < yi:
				yroute = 'out'
			elif yf > yi:
				yroute = 'in'
			else:
				yroute = 'fly'
		if yi > 26.5:
			if yf < yi:
				yroute = 'in'
			elif yf > yi:
				yroute = 'out'
			else:
				yroute = 'fly'

		# More descriptive route name
		if xroute == 'short' and yroute == 'out':
			yroute = 'flat'
		elif xroute == 'short' and yroute == 'in':
			yroute = 'slant'
		elif xroute == 'deep' and yroute == 'in':
			yroute = 'post'
		elif xroute == 'deep' and yroute == 'out':
			yroute = 'corner'

		if abs(yf - yi) < 3 and xroute == 'short':
			yroute = 'stop'
		
		print(displayName + " ran a " + xroute + " " + yroute + " route!")
		
		if receiver:
			main_df.loc[index,'xcatchingReceiverRoute'] = xroute
			main_df.loc[index,'ycatchingReceiverRoute'] = yroute
		else:
			main_df.loc[index,'xReceiverMate' + str(receiverMateCounter)] = xroute
			main_df.loc[index,'yReceiverMate' + str(receiverMateCounter)] = yroute
```

The code above will also add data for when there is a 5th or 6th additional receiver, but since that doesn't happen very often, we'll drop those columns.
```py
main_df = main_df.drop(['xReceiverMate5', 'yReceiverMate5', 'xReceiverMate6', 'yReceiverMate6'], axis=1)
```

## Add Additional Features from Raw Play Data

The following code will bring in some additional fields (```'down','yardsToGo','offenseFormation','defendersInTheBox','numberOfPassRushers','personnel.defense','personnel.offense'```) from the raw play data and merge those fields to main_df. We will use these as additional features when training the model.
```py
# Read in play data
plays = pd.read_csv(r'Data/plays.csv')
# Isolate play features to be used in training (and gameId and playId to merge to main dataset)
play_features = plays[['gameId','playId','down','yardsToGo','offenseFormation','defendersInTheBox','numberOfPassRushers','personnel.defense','personnel.offense']]

# Merge play features to main data
main_df = pd.merge(main_df, play_features,  how='left', on=['gameId','playId'])
```

## Preparing the Data for Training: One Hot Encoding

Let's start this section by creating a new python file and importing some tools we'll be using.
```py
import pandas as pd
import pickle as p
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from math import sqrt
import matplotlib.pyplot as plt
```

Also, load in main_df which we prepared and saved previously.
```py
main_df = pd.read_csv(r'derivedData/catchSeparationData.csv')
```

Here's a flow-chart to give an overview of what we'll be doing in this section.
## Preparing Data & Training KNN Model
![](http://yuml.me/diagram/plain;dir:lr;scale:150/class/[Modeling%20Dataset{bg:steelblue}]->[One%20hot%20encode%20Features],[One%20hot%20encode%20Features]->[Train-Test%20Split%20(70-30)],[Train-Test%20Split%20(70-30)]->[Min-Max%20Scaler;(Range=0%20to%201)],[Min-Max%20Scaler;(Range=0%20to%201)]->[x_train],[Min-Max%20Scaler;(Range=0%20to%201)]->[y_train],[x_train]->[K-Nearest-Neighbor%20Regressor],[y_train]->[K-Nearest-Neighbor%20Regressor],[K-Nearest-Neighbor%20Regressor]->[Final%20Trained%20Model{bg:salmon}] "yUML")

In order to train a machine learning model, we'll need to convert all of our data into numbers. The technique we're going to use for that is called One Hot Encoding. If you want to read more on this technique, check out this great article by Jason Brownlee which gives a great overview: ![Why One-Hot Encode Data in Machine Learning?](https://machinelearningmastery.com/why-one-hot-encode-data-in-machine-learning/)

First, we'll have to create a map for each categorical variable. The map is essentially a key:value dictionary where the key is the categorical variable and the value is the number we're going to use to replace that categorical variable in the data. (**__note:__** When we pass in data to our final trained model to make a prediction, we'll refer to these same mapping values to convert all of our pre-snap information into numbers that the model can understand)
```py
xmap = {'short' : 1, 'medium' : 2, 'deep' : 3}
ymap = {'stop' : 1, 'slant' : 2, 'flat' : 3, 'out' : 4, 'in' : 5, 'post' : 6, 'corner' : 7, 'fly' : 8}

oformationMap = {'SHOTGUN' : 1, 'EMPTY' : 2, 'SINGLEBACK' : 3, 'I_FORM' : 4, 'PISTOL' : 5, 'JUMBO' : 6}

dpersonnelMap = {'4 DL, 2 LB, 5 DB' : 1, \
'4 DL, 1 LB, 6 DB' : 2, \
'3 DL, 3 LB, 5 DB' : 3, \
'4 DL, 4 LB, 3 DB' : 4, \
'2 DL, 4 LB, 5 DB' : 5, \
'4 DL, 3 LB, 4 DB' : 6, \
'2 DL, 3 LB, 6 DB' : 7, \
'3 DL, 4 LB, 4 DB' : 8, \
'1 DL, 3 LB, 7 DB' : 9, \
'3 DL, 2 LB, 6 DB' : 10, \
'1 DL, 4 LB, 6 DB' : 11, \
'3 DL, 1 LB, 7 DB' : 12, \
'1 DL, 5 LB, 5 DB' : 13, \
'5 DL, 4 LB, 2 DB' : 14, \
'2 DL, 5 LB, 4 DB' : 15, \
'1 DL, 4 LB, 5 DB' : 16, \
'2 DL, 2 LB, 7 DB' : 17, \
'0 DL, 5 LB, 6 DB' : 18, \
'0 DL, 4 LB, 7 DB' : 19, \
'5 DL, 1 LB, 5 DB' : 20, \
'5 DL, 2 LB, 4 DB' : 21, \
'1 DL, 3 LB, 6 DB, 1 WR' : 22, \
'2 DL, 4 LB, 4 DB, 1 OL' : 23, \
'1 DL, 2 LB, 8 DB' : 24}

opersonnelMap = {'1 RB, 1 TE, 3 WR' : 1, \
'1 RB, 0 TE, 4 WR' : 2, \
'1 RB, 3 TE, 1 WR' : 3, \
'1 RB, 2 TE, 2 WR' : 4, \
'0 RB, 1 TE, 4 WR' : 5, \
'2 RB, 1 TE, 2 WR' : 6, \
'2 RB, 0 TE, 3 WR' : 7, \
'2 RB, 2 TE, 1 WR' : 8, \
'0 RB, 2 TE, 3 WR' : 9, \
'0 RB, 0 TE, 5 WR' : 10, \
'1 RB, 1 TE, 2 WR,1 DL' : 11, \
'3 RB, 1 TE, 1 WR' : 12, \
'1 RB, 2 TE, 1 WR,1 DL' : 13, \
'2 RB, 3 TE, 2 WR' : 14}
```

We can then replace all of the categorical values in our data with their mapped numbers like this:
```py
main_df['xReceiverMate1'] = main_df['xReceiverMate1'].map(xmap)
main_df['yReceiverMate1'] = main_df['yReceiverMate1'].map(ymap)
main_df['xReceiverMate2'] = main_df['xReceiverMate2'].map(xmap)
main_df['yReceiverMate2'] = main_df['yReceiverMate2'].map(ymap)
main_df['xReceiverMate3'] = main_df['xReceiverMate3'].map(xmap)
main_df['yReceiverMate3'] = main_df['yReceiverMate3'].map(ymap)
main_df['xReceiverMate4'] = main_df['xReceiverMate4'].map(xmap)
main_df['yReceiverMate4'] = main_df['yReceiverMate4'].map(ymap)
main_df['xcatchingReceiverRoute'] = main_df['xcatchingReceiverRoute'].map(xmap)
main_df['ycatchingReceiverRoute'] = main_df['ycatchingReceiverRoute'].map(ymap)
main_df['offenseFormation'] = main_df['offenseFormation'].map(oformationMap)
main_df['personnel.defense'] = main_df['personnel.defense'].map(dpersonnelMap)
main_df['personnel.offense'] = main_df['personnel.offense'].map(opersonnelMap)
```

## Preparing the Data for Training: Preliminary Data Analysis

Let's plot our label and features to get an idea of what our training data looks like.

```
main_df.hist(figsize=(16, 20), bins=50, xlabelsize=8, ylabelsize=8)
plt.show()
```

![Features and Labels Distributions](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/features_labels_distributions.png)

A few things that you can notice is that defense personnel is much more varied than offense personnel, hinting at a more dynamic nature to personnel choices by defensive coordinators. As expected, a relatively small portion of our data consists of 4th down plays since we are looking at completed passes only. The catch routes show positive variation for the catcing receiver as well as receiver mate routes although short passes seem much more common (indicated by x route values of 1 which we mapped to catches less than 15 yards beyond the line of scrimmage).

Let's look a little closer at our label, the catch separation in yards.

![Catch Separation Histogram](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/catch_separation_hist.png)

The most common separation between a receiver and his closest defender on completed pass plays are around 1 to 2 yards, accounting for about two-thirds of all catches in the data. As expected, completed passes with higher catch separations have decreased frequencey with catch separations of 8+ yards accounting for less than 200 catches combined.

Let's move on to splitting our data into training sets and test sets.

## Preparing the Data for Training: Train-Test Split

Let's drop any fields that are not features or labels.
```py
main_df = main_df.drop(['gameId','playId','catchingReceiver','closestCorner', 'offense', 'defense'], axis=1)
```

Now we can generate our training and testing datasets. I've used a standard 0.3 for the test_size parameter so 30% of our data will be held out from the training phase and will be used to test the model. Feel free to experiment with different train-test splits and checkout this great article by Yoel Zeldes that touches on some of the nuances in splitting your modeling data: ![The Story of a Bad Train-Test Split](https://towardsdatascience.com/the-story-of-a-bad-train-test-split-3343fcc33d2c)
```py
train , test = train_test_split(main_df, test_size = 0.3)

x_train = train.drop('catchSeparation', axis=1)
y_train = train['catchSeparation']
x_test = test.drop('catchSeparation', axis=1)
y_test = test['catchSeparation']
```

Next we'll use a Min-Max scaler with a range of 0-1. (If you're unfamiliar with Min-Max scaling, of course, I have a link to a great article. This one is from an article by Sebastian Raschka that's about scaling and normalization in general but has a great concise section on Min-Max scaling: ~[About Feature Scaling and Normalization: Min-Max Scaling](https://sebastianraschka.com/Articles/2014_about_feature_scaling.html#about-min-max-scaling)
```py
scaler = MinMaxScaler(feature_range=(0, 1))
x_train_scaled = scaler.fit_transform(x_train)
x_train = pd.DataFrame(x_train_scaled)
x_test_scaled = scaler.fit_transform(x_test)
x_test = pd.DataFrame(x_test_scaled)
```

## Training the K-Nearest-Neighbor Regression Model

Before we jump in and fit our data to a KNN model, let's try and find the most optimal k-value to use. The following code will fit the data to 50 KNN models each with a different k-value between 1 and 50. We'll then store and plot the Mean Absolute Errors and Root Mean Squared Errors for each k-value.
```py
for K in range(50):
    K = K+1
    model = neighbors.KNeighborsRegressor(n_neighbors = K)
    model.fit(x_train, y_train)  #fit the model
    pred=model.predict(x_test) #make prediction on test set
    rmse = sqrt(mean_squared_error(y_test,pred)) #calculate rmse
	rmse_vals.append(rmse) #store rmse values
	mae = mean_absolute_error(y_test, pred) #calculate mae
	mae_vals.append(mae)
    print('k= ' , K , '-----RMSE=', rmse,'-----MAE=',mae)

k_values = np.linspace(1,50)

# Plot the Root Mean Squared Error and Mean Absolute Error
plt.plot(k_values, rmse_vals, 'bx-', color='red')
plt.plot(k_values, mae_vals, 'bx-', color='blue')
plt.xlabel('k')
plt.ylabel('Root Mean Squared Error')
plt.title('Change in Root Mean Squared Error as k-value Increases')
plt.legend(['Root Mean Squared Error', 'Mean Absolute Error'], loc='upper right')
plt.show()
```

Here's a look at the plot. As you can see, the measurements of error decreases and then levels off. A k-value of 23 seems to be the point where increasing the k-value doesn't provide any more accuracy so let's go with that.

![KNN Error Graph](https://github.com/samsetegne/SSetegne-NFL-Big-Data-Bowl-Submission/blob/master/images/knn_error_graph.png)

```py
# Initialize a KNN Regressor: K value with lowest RME & MAE is 23
model = neighbors.KNeighborsRegressor(n_neighbors = 23)
```

Now all that's left to do is to train the model and serialize it to a pickle file!
```py
# Initialize a KNN Regressor: K value with lowest RME & MAE is 23
model = neighbors.KNeighborsRegressor(n_neighbors = 23)
# Fit the model to the training data
model.fit(x_train, y_train)  #fit the model
# Pickle the model
p.dump(model, open('catchSeparationModel.pkl','wb'))
```

...and that's it, the model is ready to be implemented!
