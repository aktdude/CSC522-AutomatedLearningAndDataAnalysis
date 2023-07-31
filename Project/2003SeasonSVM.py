import pandas as pd
import os
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import precision_recall_fscore_support as prfs
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def svm(xtrain, xtest, ytrain, ytest):
    C_values = [0.1, 0.2, 0.3, 1, 5, 10, 20, 100, 200, 1000]
    degree = [1, 2, 3, 4, 5]
    coef0 = [0.0001, 0.001, 0.002, 0.01, 0.02, 0.1, 0.2, 0.3, 1, 2, 5, 10]
    gamma = [0.0001, 0.001, 0.002, 0.01, 0.02, 0.03, 0.1, 0.2, 1, 2, 3]

    # linear, poly, rbf, sigmoid
    kernels = ['linear', 'poly', 'rbf', 'sigmoid']
    for k in kernels:
        parameters = {'kernel': [k], 'C': C_values}
        if k == 'poly':
            parameters['degree'] = degree
            parameters['coef0'] = coef0
        elif k == 'rbf':
            parameters['gamma'] = gamma
        elif k == 'sigmoid':
            parameters['coef0'] = coef0
            parameters['gamma'] = gamma
        svc = SVC()
        clf = GridSearchCV(svc, parameters,cv=None)
        clf.fit(xtrain, ytrain)
        print(f'best estimator for {k} is {clf.best_estimator_}')
        print(accuracy_score(ytest, clf.predict(xtest)))

def main():

    path = os.getcwd()
    path += "/Project/Datasets/Derived/games_2003.csv"
    games_2003 = pd.read_csv(path)
    print(games_2003)
    X = games_2003.drop("HOME_TEAM_WINS", axis=1)
    y = games_2003["HOME_TEAM_WINS"]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)
    svm(x_train, x_test, y_train, y_test)

if __name__ == "__main__":
    main()
