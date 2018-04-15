import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_classif
import warnings
warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)
import os

LABEL_COLUMN = 'Vote'


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
    return train.copy(), validate.copy(), test.copy()


def test_data_preparation(train_x, train_y, test_x, test_y, title):
    forest = RandomForestClassifier(n_estimators=3)
    forest = forest.fit(train_x, train_y)
    y_pred_RF = forest.predict(test_x)

    clf = SVC()
    clf = clf.fit(train_x, train_y)
    y_pred_SVM = clf.predict(test_x)

    gbc = GradientBoostingClassifier()
    gbc = gbc.fit(train_x, train_y)
    y_pred_GBC = gbc.predict(test_x)

    lr = LogisticRegression()
    lr = lr.fit(train_x, train_y)
    y_pred_LR = lr.predict(test_x)

    # print results
    print('{0:=^80}'.format(title))
    table_metrics_print(
        ['RF', 'SVM', 'GBC', 'LR'],
        np.array([
            get_metrics_list(test_y, y_pred_RF),
            get_metrics_list(test_y, y_pred_SVM),
            get_metrics_list(test_y, y_pred_GBC),
            get_metrics_list(test_y, y_pred_LR)
        ]).transpose()
    )
    print('{0:=^80}'.format(''))


def table_metrics_print(header, data):
    print(pd.DataFrame(data, ["Accuracy", "Precision", "Recall", "F1"], header))


def get_metrics_list(y_true, y_pred):
    return [
        metrics.accuracy_score(y_true, y_pred),
        metrics.precision_score(y_true, y_pred, average='weighted',),
        metrics.recall_score(y_true, y_pred, average='weighted'),
        metrics.f1_score(y_true, y_pred, average='weighted')
    ]


def handle_outliers(train, validate, test):
    # TODO improve - currently ignore outliers
    return train, validate, test


def handle_imputation(train, validate, test):
    # TODO improve - currently imputes mode to categorical and mean to numerical
    category_features = train.select_dtypes(include='category').columns

    for f in train:
        value = train[f].dropna().mode() if f in category_features else train[f].dropna().mean()

        impute(train, f, value)
        impute(validate, f, value)
        impute(test, f, value)

    return train, validate, test


def impute(dataframe, f, value):
    dataframe.loc[dataframe[f].isnull(), f] = value


def handle_scaling(train, validate, test):
    # TODO improve - currently uses standard distribution scaler, only using train data.
    # TODO Pay attention to bonus assignment - asks to first use ALL data, then compare to only train
    scaler = StandardScaler()

    non_label_features = train.keys()[train.columns.values != LABEL_COLUMN]

    scaler.fit(train[non_label_features])

    train[non_label_features] = scaler.transform(train[non_label_features])
    validate[non_label_features] = scaler.transform(validate[non_label_features])
    test[non_label_features] = scaler.transform(test[non_label_features])

    return train, validate, test


def handle_feature_selection(train, validate, test):
    # TODO improve - currently uses select k best, only using train data.
    # TODO Pay attention to bonus assignment - asks to first use ALL data, then compare to only train
    # TODO Pay attention to k=19. Try other k's?

    train_x, train_y = split_label(train)

    univariate_filter = SelectKBest(mutual_info_classif, k=19).fit(train_x, train_y)

    train = transform(univariate_filter, train)
    validate = transform(univariate_filter, validate)
    test = transform(univariate_filter, test)

    return train, validate, test


def split_label(dataframe):
    return dataframe.drop([LABEL_COLUMN], axis=1), dataframe.Vote


def transform(selector, dataframe):
    return dataframe[
        (dataframe.drop([LABEL_COLUMN], axis=1).columns[selector.get_support()]).append(pd.Index([LABEL_COLUMN]))
    ]


def identify_and_set_feature_type(dataframe):
    object_features = dataframe.select_dtypes(include='object').columns

    for f in object_features:
        dataframe[f] = dataframe[f].astype('category')


def handle_type_modification(train, validate, test):
    # TODO improve? Meaning turning non numeric types to numeric?
    # improve ideas - ordered-keep as is. un ordered- dummy features?
    category_features = train.select_dtypes(include='category').columns.values

    for f in category_features:
        if f != LABEL_COLUMN:
            train[f] = train[f].cat.codes
            validate[f] = validate[f].cat.codes
            test[f] = test[f].cat.codes

    return train, validate, test


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

    identify_and_set_feature_type(df)

    train, validate, test = train_validate_test_split(df)

    save_as_csv_original(train, validate, test)

    train, validate, test = handle_outliers(train, validate, test)
    train, validate, test = handle_imputation(train, validate, test)
    train, validate, test = handle_type_modification(train, validate, test)
    train, validate, test = handle_scaling(train, validate, test)
    train, validate, test = handle_feature_selection(train, validate, test)

    save_as_csv(train, validate, test)


def test_results():
    train = pd.read_csv('train_original.csv', header=0)
    validate = pd.read_csv('validate_original.csv', header=0)
    test = pd.read_csv('test_original.csv', header=0)
    train, validate, test = most_basic_preparation(train, validate, test)
    train_x, train_y = split_label(train)
    test_x, test_y = split_label(test)
    test_data_preparation(train_x, train_y, test_x, test_y, 'Basic')

    train = pd.read_csv('train.csv', header=0)
    test = pd.read_csv('test.csv', header=0)
    train_x, train_y = split_label(train)
    test_x, test_y = split_label(test)
    test_data_preparation(train_x, train_y, test_x, test_y, 'Advanced')


def most_basic_preparation(train, validate, test):
    train_x, _ = split_label(train)
    object_features = train_x.select_dtypes(include='object').columns.values

    train = train.drop(object_features, axis=1).dropna()
    validate = validate.drop(object_features, axis=1).dropna()
    test = test.drop(object_features, axis=1).dropna()

    return train, validate, test


if __name__ == '__main__':
    prepare_data()
    test_results()

