import pandas as pd
import numpy as np
from DataCollection.cleaning.MissingDataHandler import MissingDataHandler

def test_it_fills_missing_fields():
    data = pd.DataFrame({
        'numerical_field': [1, 2, 3, np.nan, 5],
        'categorical_field': ['a', 'b', 'c', np.nan, 'e']
    })

    missing_data_handler = MissingDataHandler()

    processed_data = missing_data_handler.handle_missing_data(data)

    assert processed_data['numerical_field'].isnull().sum() == 0