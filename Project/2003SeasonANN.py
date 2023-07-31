import numpy as np
import pandas as pd
import tensorflow as tf
import os
import random
import sklearn.metrics as metrics
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

path = os.getcwd()
path += "/Project/Datasets/Derived/games_2003.csv"
games_2003 = pd.read_csv(path)
X = games_2003.drop("HOME_TEAM_WINS", axis=1)
y = games_2003["HOME_TEAM_WINS"]

print(X)

x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)

os.environ['PYTHONHASHSEED']='2022'
np.random.seed(2022)
tf.random.set_seed(2022)
random.seed(2022)

accuracyMatrixValidate = {}
accuracyMatrixTrain = {}

inputSize = len(games_2003.columns)

# Size Values
X = [100,110,120,125, 130, 140, 150, 160, 170, 180, 190, 200]
for x in X:
    # Initializing ANN
    ann = tf.keras.models.Sequential()
    # Creating input layer and first hidden layer
    ann.add(tf.keras.layers.Dense(x, activation='relu', input_shape = (inputSize - 1, )))
    # Creating the output layer
    ann.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    #Setting the Optimizer, metrics and loss function.
    ann.compile(loss=tf.keras.losses.binary_crossentropy, optimizer='adam',metrics=['accuracy'] )
    # Fitting the Model to the training data with batch size 10 and epochs 5
    ann.fit(x_train, y_train, batch_size=10,  epochs = 5)
    # Predicing Validation data
    yPredictTest = ann.predict(x_test)
    # Predicing Testing data
    yPredictTrain = ann.predict(x_train)
    # If the value is greater than 0.5 we want it to be true (or 1)
    yPredictTest = (yPredictTest > 0.5)
    yPredictTrain = (yPredictTrain > 0.5)
    # Calculating accuracy for validation data
    a = accuracy_score(y_test,yPredictTest)
    # Calculating accuracy for training data
    b = accuracy_score(y_train,yPredictTrain)
    #Storing values in map
    accuracyMatrixValidate[x] = a
    accuracyMatrixTrain[x] = b

# Plotting the accuracy wrt number of hidden neurons in the hidden layer
# For The Label, V mean validation and T means Training
fig = plt.figure()
ScatterPlot = fig.add_subplot()
ScatterPlot.scatter(accuracyMatrixValidate.keys(),accuracyMatrixValidate.values() , c ='red')
ScatterPlot.scatter(accuracyMatrixTrain.keys(),accuracyMatrixTrain.values() , c ='blue')
ScatterPlot.set_title("Accuracy wrt Number of Neurons in the hidden layer")
ScatterPlot.set_xlabel("Number of Neurons in the Hidden Layer")
ScatterPlot.set_ylabel("Accuracy")
ScatterPlot.legend("VT")

plt.show()

