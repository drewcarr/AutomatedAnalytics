import pandas as pd
import pytest
from DataCollection.cleaning.Normalizer import Normalizer

def test_normalize():
    data = pd.DataFrame({
        'feature1': [1.0, 2.0, 3.0, 4.0],
        'feature2': [10, 20, 30, 40]
    })

    normalizer = Normalizer()
    normalized_data = normalizer.normalize(data)

    # Check if the mean of each column is approximately 0 and the standard deviation is close to 1
    assert normalized_data['feature1'].mean() == pytest.approx(0, abs=1e-6)
    assert normalized_data['feature1'].std() == pytest.approx(1, abs=2e-1)
    assert normalized_data['feature2'].mean() == pytest.approx(0, abs=1e-6)
    assert normalized_data['feature2'].std() == pytest.approx(1, abs=2e-1)