from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from sklearn.metrics import mean_squared_error
from math import sqrt
import matplotlib.pyplot as plt

xmap = {'short' : 1, 'medium' : 2, 'deep' : 3}
ymap = {'stop' : 1, 'slant' : 2, 'flat' : 3, 'out' : 4, 'in' : 5, 'post' : 6, 'corner' : 7, 'fly' : 8}

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

rmse_val = []

for K in range(20):
    K = K+1
    model = neighbors.KNeighborsRegressor(n_neighbors = K)

    model.fit(x_train, y_train)  #fit the model
    pred=model.predict(x_test) #make prediction on test set
    error = sqrt(mean_squared_error(y_test,pred)) #calculate rmse
    rmse_val.append(error) #store rmse values
    print('RMSE value for k= ' , K , 'is:', error)
	
# K value with lowest RME is 14
model = neighbors.KNeighborsRegressor(n_neighbors = 14)
model.fit(x_train, y_train)  #fit the model

predict = model.predict(x_test)