import pandas as pd

from DataCleaning.DataCleaningPipeline import DataCleaningPipeline

class DataCleaner:
    def __init__(self):
        self.data_cleaning_pipeline = DataCleaningPipeline()

    def clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        print('Cleaning data...')

        return self.data_cleaning_pipeline.process(raw_data)