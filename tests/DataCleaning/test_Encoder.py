import pandas as pd
from DataCleaning.Encoder import Encoder

def test_encode():
    data = pd.DataFrame({
        'feature_name': ['a', 'b', 'a', 'c']
    })

    encoder = Encoder()
    encoded_data = encoder.encode(data)

    expected_columns = ['feature_name_a', 'feature_name_b', 'feature_name_c']

    expected_values = [
        [1, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1]
    ]
    assert encoded_data[expected_columns].values.tolist() == expected_values

def test_encode_boolean():
    data = pd.DataFrame({
        'boolean_feature': [True, False, True, False]
    })

    encoder = Encoder()
    encoded_data = encoder.encode(data)

    expected_values = [1, 0, 1, 0]
    assert encoded_data['boolean_feature'].tolist() == expected_values

def test_encode_datetime():
    data = pd.DataFrame({
        'date_feature': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'])
    })

    encoder = Encoder()
    encoded_data = encoder.encode(data)

    expected_data = pd.DataFrame({
        'date_feature_year': pd.Series([2023, 2023, 2023, 2023], dtype='int32'),
        'date_feature_month': pd.Series([1, 1, 1, 1], dtype='int32'),
        'date_feature_day': pd.Series([1, 2, 3, 4], dtype='int32'),
        'date_feature_hour': pd.Series([0, 0, 0, 0], dtype='int32'),
        'date_feature_day_of_week': pd.Series([6, 0, 1, 2], dtype='int32')
    })

    pd.testing.assert_frame_equal(encoded_data, expected_data)

def test_encode_timedelta():
    data = pd.DataFrame({
        'timedelta_feature': pd.to_timedelta(['1 days', '2 days', '3 days', '4 days'])
    })

    encoder = Encoder()
    encoded_data = encoder.encode(data)

    expected_values = [1, 2, 3, 4]
    assert encoded_data['timedelta_feature'].tolist() == expected_values