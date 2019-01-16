import pandas as pd
import matplotlib.pyplot as plt
import sys

if len(sys.argv) < 4:
    print("Missing Arguments: 3 arguments expected but only " + str(len(sys.argv) - 1) + " arguments provided.")
    print("Please pass in player's full name, the game's ID number, and the play's ID, in that order.")
elif len(sys.argv) > 4:
    print("Too Many Arguments: 3 arguments expected but " + str(len(sys.argv) - 1) + " arguments provided.")
    print("Please pass in only the player's full name, the game's ID number, and the play's ID, in that order.")

dfgame = pd.read_csv(r'Data/tracking_gameId_' + str(sys.argv[2]) + '.csv')
    
x = dfgame[(dfgame['displayName'] == sys.argv[1]) & (dfgame['playId'] == int(sys.argv[3])) & (dfgame['gameId'] == int(sys.argv[2]))]['x'].values
y = dfgame[(dfgame['displayName'] == sys.argv[1]) & (dfgame['playId'] == int(sys.argv[3])) & (dfgame['gameId'] == int(sys.argv[2]))]['y'].values

print("Painting route shape for " + sys.argv[1] + "'s route during play " + str(sys.argv[3]) + "" + str(sys.argv[2]) + " in game ")
plt.plot(x,y, 'ro')

# To show route with the graph axes set to a football field
#plt.axis([0, 120, 0, 54])

# To zoom axes so route fills up graph
plt.axis('equal')

plt.show()