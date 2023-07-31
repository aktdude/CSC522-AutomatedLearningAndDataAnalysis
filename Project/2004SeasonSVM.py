import pandas as pd
import os
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import precision_recall_fscore_support as prfs
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def svm2003(xtrain, xtest, ytrain, ytest):
    svc = SVC(kernel="poly", C=0.1, coef0=0.0001, degree=5)
    svc.fit(xtrain, ytrain)
    print(accuracy_score(ytest, svc.predict(xtest)))

def main():

    path = os.getcwd()
    path += "/Project/Datasets/Derived/games_2004.csv"
    games_2004 = pd.read_csv(path)
    print(games_2004)
    X = games_2004.drop("HOME_TEAM_WINS", axis=1)
    y = games_2004["HOME_TEAM_WINS"]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)
    svm2003(x_train, x_test, y_train, y_test)

if __name__ == "__main__":
    main()
