
import unittest
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import SelectFromModel
import argparse
import mlflow.sklearn
from azureml.core import Workspace, Dataset
import os

mlflow.autolog()

class TestMLPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        # Load the workspace
        ws = Workspace.from_config()
        # Get a dataset by its name from the workspace
        test_dataset = Dataset.get_by_name(ws, name='test', version='latest')
        train_dataset = Dataset.get_by_name(ws, name='train', version='latest')

        cls.train_dataset = train_dataset.to_pandas_dataframe()
        cls._test_dataset = test_dataset.to_pandas_dataframe()



        # Get dataset paths from environment variables set by Azure ML
        #training_data_path = os.getenv('AZUREML_DATAREFERENCE_training_data')
        #testing_data_path = os.getenv('AZUREML_DATAREFERENCE_test_dataset')

        # Load datasets
        #cls.train_dataset = pd.read_csv(training_data_path) if training_data_path else None
        #cls.test_dataset = pd.read_csv(testing_data_path) if testing_data_path else None

        # Load the dataset
        #cls.train_dataset = pd.read_csv(r"C:\Users\user\Documents\COM774_CW2\production\test_dataset.csv")
        #cls.test_dataset = pd.read_csv(r"C:\Users\user\Documents\COM774_CW2\production\test_dataset.csv")

        #cls.workspace = Workspace.from_config()
        
        # Load the datasets using Azure ML Dataset
        #cls.test_dataset = Dataset.get_by_name(cls.workspace, name='test', version='1').to_pandas_dataframe()   

    def test_label_encoding(self):
        label_encoder = LabelEncoder()
        self.test_dataset['Activity'] = label_encoder.transform(self.test_dataset['Activity'])
        self.assertIn('Activity', self.train_dataset.columns)
        self.assertIn('Activity', self.test_dataset.columns)

    def test_label_encoding(self):
        label_encoder = LabelEncoder()
        # Fit the encoder on the training dataset
        self.train_dataset['Activity'] = label_encoder.fit_transform(self.train_dataset['Activity'])
        # Now transform the test dataset
        try:
            self.test_dataset['Activity'] = label_encoder.transform(self.test_dataset['Activity'])
        except Exception as e:

            self.fail(f"Label encoding failed: {e}")
        self.assertIn('Activity', self.train_dataset.columns)
        self.assertIn('Activity', self.test_dataset.columns)


    def test_data_split(self):
        features = self.train_dataset.drop(['Activity', 'subject'], axis=1)
        labels = self.train_dataset['Activity']
        X_train, X_val, y_train, y_val = train_test_split(features, labels, test_size=0.3, random_state=42)
        self.assertEqual(len(X_train) + len(X_val), len(features))

    def test_model_training_and_evaluation(self):
        features = self.train_dataset.drop(['Activity', 'subject'], axis=1)
        labels = self.train_dataset['Activity']
        X_train, X_val, y_train, y_val = train_test_split(features, labels, test_size=0.3, random_state=42)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)

        rf = RandomForestClassifier(random_state=42)
        rf.fit(X_train, y_train)
        y_val_pred = rf.predict(X_val)
        accuracy = accuracy_score(y_val, y_val_pred)
        self.assertTrue(0 <= accuracy <= 1)

        # Evaluate using classification report (additional check)
        report = classification_report(y_val, y_val_pred, output_dict=True)
        self.assertIn('accuracy', report)

    def test_feature_selection(self):
        features = self.train_dataset.drop(['Activity', 'subject'], axis=1)
        labels = self.train_dataset['Activity']
        X_train, _, y_train, _ = train_test_split(features, labels, test_size=0.3, random_state=42)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)

        rf = RandomForestClassifier(random_state=42)
        rf.fit(X_train, y_train)
        selector = SelectFromModel(rf, prefit=True)
        X_train_selected = selector.transform(X_train)
        self.assertTrue(X_train_selected.shape[1] <= X_train.shape[1])

if __name__ == '__main__':
    unittest.main()
