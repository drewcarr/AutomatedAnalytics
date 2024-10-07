import pandas as pd
from sklearn.preprocessing import OneHotEncoder

class Encoder:
    def __init__(self):
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.categorical_column_identifiers = ['object']

    def encode(self, data: pd.DataFrame) -> pd.DataFrame:
        categorical_cols = data.select_dtypes(include=self.categorical_column_identifiers).columns
        if not categorical_cols.empty:
            encoded_features = self.encoder.fit_transform(data[categorical_cols])
            encoded_df = pd.DataFrame(encoded_features, columns=self.encoder.get_feature_names_out(categorical_cols))
            return pd.concat([data.drop(columns=categorical_cols), encoded_df], axis=1)
        else:
            return data