import pandas as pd
import numpy as np

#sklearn libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


class BC_Predict:

    def has_disease(self, row):
        self.train(self)
        # return 2 if benign, return 4 if malign
        return True if self.predict(self, row) == 4 else False

    @staticmethod
    def train(self):
        # read dataset
        dataset = pd.read_csv('dataSet/breast-cancer.csv')
        
        # clear dataset
        dataset = dataset[dataset.Bare_Nuclei != '?'] # one of the data is invalid
        
        # drop unnecessary id
        dataset = dataset.drop(['Sample code number'], axis=1)
        y = dataset['Class']

        # class shows us patient is malign or benign
        X = dataset.drop(['Class'], axis=1)

        # Split DataSet %33 for test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=13)

        # Random Forest Algorithm
        self.classifier = RandomForestClassifier(n_estimators=10, criterion='entropy', random_state=0)
        self.classifier.fit(X_train, y_train)
        score = self.classifier.score(X_test, y_test)

        # Prediction Score %95
        #print('Score: ' + str(score))

    @staticmethod
    def predict(self, row):
        user_df = np.array(row).reshape(1, 9)
        predicted = self.classifier.predict(user_df)

        return predicted[0]


# Test Function
def test(data):

    predictor = BC_Predict()
    result = predictor.has_disease(data)

    if (result == True):
        #Person Have Breast Cancer
        return 0
    else:
        # Person Is Healthy
        return 1