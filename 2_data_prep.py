import pandas as pd
import pickle as p
from scipy.spatial import distance
import math

# Function to find the closest point from an array of points
def closest_node(center_point, surrounding_points):
    '''
    center_point: Pass in a point as a tuple of (x, y)
    surrounding_points: Pass in points as an array of (x, y) points to compare
    Function will return the point within the surrounding_points array that's closest to center_point
    '''
    closest_index = distance.cdist([center_point], surrounding_points).argmin()
    return surrounding_points[closest_index]

# Function to calculate the distance between two points
def calculateDistance(x1,y1,x2,y2):  
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist

def addCatchSeparation(dfcatch):
    # Create a tuple containing the balls x,y coordinates
    ball_point = (dfcatch[(dfcatch['team']=='ball')]['x'].values[0], dfcatch[(dfcatch['team']=='ball')]['y'].values[0])

    # Filter the catch frame data to only players data
    dfcatch_players = dfcatch[(dfcatch['team'] != 'ball')]

    # Convert the players points to an array
    player_points = dfcatch_players[['x','y']].values

    # Calculate the coordinates of the closest player to the ball (Receiver who caught the ball)
    closest_player_coordinates = closest_node(ball_point, player_points)

    # Filter the catch frame data to those coordinates to identify the receiver who caught the ball
    catch_player = dfcatch[(dfcatch['x'] == closest_player_coordinates[0]) & (dfcatch['y'] == closest_player_coordinates[1])]

    # Find the team of the player who caught the ball
    team = catch_player['team'].values[0]

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

    # Calculate the distance between the receiver and the corner (or closest player on the other team)
    # Distance object type is float and the units are yards
    corner_distance = calculateDistance(catch_player['x'].values[0], catch_player['y'].values[0], defending_corner['x'].values[0], defending_corner['y'].values[0])
    
    # Create a copy of dfcatch
    dfcatch_wSeparation = dfcatch
    
    # Add the distance of the closest player to the receiver to a field called catchSeparation
    dfcatch_wSeparation['catchSeparation'] = corner_distance
    dfcatch_wSeparation['catchingReceiver'] = catch_player['displayName'].values[0]
    dfcatch_wSeparation['closestCorner'] = defending_corner['displayName'].values[0]
    
    
    return dfcatch_wSeparation
	
# Load cached dictionary containing dataframes of each game
games = p.load(open(r'derivedData/games.pkl', 'rb'))
	
######################################
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
	
# Output the result to a csv file
#main_df.to_csv('derivedData/catchSeparationData.csv', index=False)

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
			
# Drop 5th and 6th additional receiver data which is rarely applicable
main_df = main_df.drop(['xReceiverMate5', 'yReceiverMate5', 'xReceiverMate6', 'yReceiverMate6'], axis=1)

# Select only the rows where the following columns have no null values
# xReceiverMate1, yReceiverMate1, xReceiverMate2, yReceiverMate2, xReceiverMate3, yReceiverMate3, xReceiverMate4, yReceiverMate4, xcatchingReceiverRoute, ycatchingReceiverRoute, catchSeparation
main_df = main_df[main_df.xReceiverMate4.notnull()][main_df.xReceiverMate3.notnull()][main_df.xReceiverMate2.notnull()][main_df.xReceiverMate1.notnull()][main_df.yReceiverMate4.notnull()][main_df.yReceiverMate3.notnull()][main_df.yReceiverMate2.notnull()][main_df.yReceiverMate1.notnull()][main_df.xcatchingReceiverRoute.notnull()][main_df.ycatchingReceiverRoute.notnull()][main_df.catchSeparation.notnull()]

# Output the result to a csv file
#main_df.to_csv(r'derivedData/catchSeparationData.csv', index=False)