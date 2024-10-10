from DataCollection.cleaning.Encoder import Encoder
from DataCollection.cleaning.MissingDataHandler import MissingDataHandler
from DataCollection.cleaning.Normalizer import Normalizer

class DataCleaningPipeline:
    def __init__(self):
        self.missing_data_handler = MissingDataHandler()
        self.encoder = Encoder()
        self.normalizer = Normalizer()
        self.steps = [
            (self.missing_data_handler, 'handle_missing_data'),
            (self.normalizer, 'normalize'),
            (self.encoder, 'encode')
        ]

    def process(self, data):
        for step, method_name in self.steps:
            print(f'Processing step: {method_name}')
            method = getattr(step, method_name)
            data = method(data)
        return data