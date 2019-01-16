import pandas as pd
import pickle as p

# Cache data for all games in a dictionary to optimize subsequent code
dfgames = pd.read_csv(r'Data/games.csv')
games = {}
for gameId in dfgames['gameId']:
	games[gameId] = pd.read_csv(r'Data/tracking_gameId_' + str(gameId) + '.csv')
	print("Data for game " + str(gameId) + " saved...")
	
p.dump(games, open(r'derivedData/games.pkl','wb'))