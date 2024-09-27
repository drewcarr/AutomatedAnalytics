# DataValidator class for validating collected data
class DataValidator:
    def validate_data(self, collected_data: dict):
        if "raw_data" in collected_data:
            return True, "Validation passed."
        return False, "Validation failed."