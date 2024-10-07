import pandas as pd
from DataCollection.cleaning.Encoder import Encoder

def test_encode():
    data = pd.DataFrame({
        'feature_name': ['a', 'b', 'a', 'c']
    })

    encoder = Encoder()
    encoded_data = encoder.encode(data)

    expected_columns = ['feature_name_a', 'feature_name_b', 'feature_name_c']
    assert all(col in encoded_data.columns for col in expected_columns)
    assert encoded_data.shape[1] == len(expected_columns)