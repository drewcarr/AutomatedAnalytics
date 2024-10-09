from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class DataRequirements:
    # The main requirement summarized from the user, expecting a couple sentences
    requirement: Optional[str] = None
    # The timeframe for the data, specifying the period of interest
    timeframe: Optional[str] = None
    # The granularity of the data, such as daily, monthly, etc.
    granularity: Optional[str] = None
    # The domain or context for the data, e.g., finance, sports
    domain_context: Optional[str] = None
    # Filters to apply to the data, represented as key-value pairs
    filters: Dict[str, str] = field(default_factory=dict)
    # Preferences for which data sources to use, e.g., specific APIs or websites
    data_source_preferences: Optional[str] = None
    # A flag indicating whether all necessary requirements have been gathered
    requirements_gathered: bool = False

    # Class-level constant for allowed fields
    ALLOWED_FIELDS = ["requirement", "timeframe", "granularity", "domain_context", "filters", "data_source_preferences", "requirements_gathered"]

    def set_fields(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.ALLOWED_FIELDS:
                if key == "requirement" and isinstance(value, str):
                    self.requirement = value.strip()
                elif key == "filters" and isinstance(value, dict):
                    if all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
                        self.filters.update(value)
                    else:
                        raise ValueError("All keys and values in 'filters' must be strings.")
                else:
                    setattr(self, key, value)
            else:
                raise ValueError(f"Field '{key}' is not a valid field of DataRequirements. Allowed fields are: {', '.join(self.ALLOWED_FIELDS)}")

    def validate_requirements(self):
        if not self.requirement:
            raise ValueError("Requirement must be specified.")
        if not self.requirements_gathered:
            raise ValueError("Requirements must be marked as gathered.")
        if self.timeframe is not None and not isinstance(self.timeframe, str):
            raise ValueError("Timeframe must be a string.")
        if self.granularity is not None and not isinstance(self.granularity, str):
            raise ValueError("Granularity must be a string.")
        if self.domain_context is not None and not isinstance(self.domain_context, str):
            raise ValueError("Domain context must be a string.")
        if not isinstance(self.filters, dict):
            raise ValueError("Filters must be a dictionary with string keys and values.")
        if self.data_source_preferences is not None and not isinstance(self.data_source_preferences, str):
            raise ValueError("Data source preferences must be a string.")

    def set_requirements_gathered(self, status: bool):
        self.requirements_gathered = status