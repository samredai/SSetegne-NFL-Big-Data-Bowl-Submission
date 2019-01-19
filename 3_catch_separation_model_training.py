import pandas as pd
import numpy as np
import pickle as p
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from math import sqrt
import matplotlib.pyplot as plt

# Load main_df data exported at the end of 2_data_prep.py
main_df = pd.read_csv(r'derivedData/catchSeparationData.csv')

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

main_df = main_df.drop(['gameId','playId','catchingReceiver','closestCorner', 'offense', 'defense'], axis=1)

train , test = train_test_split(main_df, test_size = 0.3)

x_train = train.drop('catchSeparation', axis=1)
y_train = train['catchSeparation']
x_test = test.drop('catchSeparation', axis=1)
y_test = test['catchSeparation']

scaler = MinMaxScaler(feature_range=(0, 1))
x_train_scaled = scaler.fit_transform(x_train)
x_train = pd.DataFrame(x_train_scaled)
x_test_scaled = scaler.fit_transform(x_test)
x_test = pd.DataFrame(x_test_scaled)

rmse_vals = []
mae_vals = []

for K in range(50):
    K = K+1
    model = neighbors.KNeighborsRegressor(n_neighbors = K)
    model.fit(x_train, y_train)  #fit the model
    pred = model.predict(x_test) #make prediction on test set
    rmse = sqrt(mean_squared_error(y_test,pred)) #calculate rmse
    rmse_vals.append(rmse) #store rmse values
    mae = mean_absolute_error(y_test, pred) #calculate mae
    mae_vals.append(mae)
    print('k= ' , K , '-----RMSE=', rmse,'-----MAE=',mae)

k_values = np.linspace(1,50)

# Plot the Root Mean Squared Error and Mean Absolute Error
'''
plt.plot(k_values, rmse_vals, 'bx-', color='red')
plt.plot(k_values, mae_vals, 'bx-', color='blue')
plt.xlabel('k')
plt.ylabel('Root Mean Squared Error')
plt.title('Change in Root Mean Squared Error as k-value Increases')
plt.legend(['Root Mean Squared Error', 'Mean Absolute Error'], loc='upper right')
plt.show()
'''

# Initialize a KNN Regressor: K value with lowest RME & MAE is 23
model = neighbors.KNeighborsRegressor(n_neighbors = 23)

# Fit the model to the training data
model.fit(x_train, y_train)  #fit the model

# Pickle the model
#p.dump(model, open('catchSeparationModel.pkl','wb'))