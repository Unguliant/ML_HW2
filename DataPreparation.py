import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

import os


def read_data(online):
    if online:
        return pd.read_csv(
            'https://webcourse.cs.technion.ac.il/236756/Spring2018/ho/WCFiles/ElectionsData.csv?7959',
            header=0
        )
    else:
        return pd.read_csv('ElectionsData.csv', header=0)


def train_validate_test_split(dataframe):
    train_validate, test = train_test_split(dataframe, test_size=0.2)
    train, validate = train_test_split(train_validate, test_size=0.25)
    return train, validate, test


def rank_data_preparation(train_x, train_y, validate_x, validate_y):
    kf = KFold(n_splits=5)

    data_x = pd.concat(train_x, validate_x)
    data_y = pd.concat(train_y, validate_y)

    for k, (train_index, test_index) in enumerate(kf.split(data_x)):
        # Random Forest
        # Create the random forest object which will include all the parameters
        # for the fit
        forest = RandomForestClassifier(n_estimators=3)
        # Fit the training data to the Survived labels and create the decision trees
        forest = forest.fit(data_x[train_index], data_y[train_index])
        # output = forest.predict(test_data_noNaN)
        y_pred_RF = forest.predict(data_x[test_index])

        # SVM
        # train a SVM classifier:
        clf = SVC()
        clf = clf.fit(data_x[train_index], data_y[train_index])
        # output = clf.predict(test_data_noNaN)
        y_pred_SVM = clf.predict(data_x[test_index])

        # results
        print("[fold {0}] RF score: {1:.5}, SVM score: {2:.5}".
              format(k, metrics.accuracy_score(data_y[test_index], y_pred_RF),
                     metrics.accuracy_score(data_y[test_index], y_pred_SVM)))


def test_data_preparation(train_x, train_y, test_x, test_y):
    forest = RandomForestClassifier(n_estimators=3)
    forest = forest.fit(train_x, train_y)
    y_pred_RF = forest.predict(test_x)

    clf = SVC()
    clf = clf.fit(train_x, train_y)
    y_pred_SVM = clf.predict(test_x)

    # results
    print("RF score: {0:.5}, SVM score: {1:.5}".
          format(metrics.accuracy_score(test_y, y_pred_RF),
                 metrics.accuracy_score(test_y, y_pred_SVM)))


def handle_outliers(train, validate, test):
    # TODO improve - currently ignore outliers
    return


def handle_imputation(train, validate, test):
    # TODO improve - currently imputes mode to categorical and mean to numerical
    object_features = train.keys()[train.dtypes.map(lambda x: x == 'object')]

    for f in train:
        value = train[f].dropna().mode() if f in object_features else train[f].dropna().mean()

        impute(train, f, value)
        impute(validate, f, value)
        impute(test, f, value)


def impute(dataframe, f, value):
    dataframe.loc[dataframe[f].isnull(), f] = value


def handle_scaling(train, validate, test):
    # TODO improve - currently uses standard distribution scaler, only using train data.
    # TODO Pay attention to bonus assignment - asks to first use ALL data, then compare to only train
    scaler = StandardScaler()
    scaler.fit(train)

    train[:] = scaler.transform(train)
    validate[:] = scaler.transform(validate)
    test[:] = scaler.transform(test)


def handle_feature_selection(train, validate, test):
    # TODO implement
    return


def identify_and_set_feature_type(train, validate, test):
    # TODO implement. Dafuq this means?
    return


def handle_type_modification(train, validate, test):
    # TODO implement. Meaning turning non numeric types to numeric?
    return


def save_as_csv_original(train, validate, test):
    train.to_csv("train_original.csv", index=False)
    validate.to_csv("validate_original.csv", index=False)
    test.to_csv("test_original.csv", index=False)


def save_as_csv(train, validate, test):
    # TODO ask about filenames expected
    train.to_csv("train.csv", index=False)
    validate.to_csv("validate.csv", index=False)
    test.to_csv("test.csv", index=False)


def prepare_data():
    df = read_data(online=False)

    train, validate, test = train_validate_test_split(df)

    save_as_csv_original(train, validate, test)

    handle_outliers(train, validate, test)
    handle_imputation(train, validate, test)
    handle_type_modification(train, validate, test)
    handle_scaling(train, validate, test)
    handle_feature_selection(train, validate, test)

    save_as_csv(train, validate, test)


if __name__ == '__main__':
    prepare_data()






