import pandas as pd
from sklearn.preprocessing import StandardScaler

class Normalizer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.numerical_column_types = ['float64', 'int64']

    def normalize(self, data: pd.DataFrame) -> pd.DataFrame:
        numerical_features = data.select_dtypes(include=self.numerical_column_types).columns
        data[numerical_features] = self.scaler.fit_transform(data[numerical_features])
        return data