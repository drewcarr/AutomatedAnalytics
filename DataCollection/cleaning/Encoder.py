import pandas as pd
from sklearn.preprocessing import OneHotEncoder

class Encoder:
    def __init__(self):
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.categorical_column_identifiers = ['object']
        self.boolean_column_identifier = ['bool']
        self.date_column_identifier = ['datetime64', 'timedelta64']

    def encode(self, data: pd.DataFrame) -> pd.DataFrame:
        categorical_cols = data.select_dtypes(include=self.categorical_column_identifiers).columns
        boolean_cols = data.select_dtypes(include=self.boolean_column_identifier).columns
        date_cols = data.select_dtypes(include=self.date_column_identifier).columns

        if not categorical_cols.empty:
            encoded_features = self.encoder.fit_transform(data[categorical_cols])
            encoded_df = pd.DataFrame(encoded_features, columns=self.encoder.get_feature_names_out(categorical_cols))
            data = pd.concat([data.drop(columns=categorical_cols), encoded_df], axis=1)

        if not boolean_cols.empty:
            data[boolean_cols] = data[boolean_cols].astype(int)

        if not date_cols.empty:
            for col in date_cols:
                data = _encode_date_columns(data, col)

        return data

def _encode_date_columns(data: pd.DataFrame, column: str) -> pd.DataFrame:
    if data[column].dtype == 'timedelta64[ns]':
        data[column] = data[column].apply(lambda x: x.days)
    else:
        data[f'{column}_year'] = data[column].dt.year
        data[f'{column}_month'] = data[column].dt.month
        data[f'{column}_day'] = data[column].dt.day
        data[f'{column}_hour'] = data[column].dt.hour
        data[f'{column}_day_of_week'] = data[column].dt.dayofweek
        data = data.drop(columns=[column])
    return data

