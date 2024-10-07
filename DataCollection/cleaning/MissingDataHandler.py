import pandas as pd
from sklearn.impute import SimpleImputer

class MissingDataHandler:
    def __init__(self):
        self.numerical_imputer = SimpleImputer(strategy='mean')
        self.categorical_imputer = SimpleImputer(strategy='most_frequent')
        self.numerical_column_identifiers = ['float64', 'int64']
        self.categorical_column_identifiers = ['object']

    def handle_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        numerical_cols = data.select_dtypes(include=self.numerical_column_identifiers).columns
        categorical_cols = data.select_dtypes(include=self.categorical_column_identifiers).columns

        data[numerical_cols] = self.numerical_imputer.fit_transform(data[numerical_cols])

        data[categorical_cols] = self.categorical_imputer.fit_transform(data[categorical_cols])

        return data