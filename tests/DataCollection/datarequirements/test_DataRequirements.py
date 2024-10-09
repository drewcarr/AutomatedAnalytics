import pytest
from DataCollection.DataRequirements import DataRequirements

def test_initialization():
    data_req = DataRequirements()
    assert data_req.requirement is None
    assert data_req.timeframe is None
    assert data_req.granularity is None
    assert data_req.domain_context is None
    assert data_req.filters == {}
    assert data_req.data_source_preferences is None
    assert not data_req.requirements_gathered

def test_set_fields_valid():
    data_req = DataRequirements()
    data_req.set_fields(requirement="Get sales data", timeframe="2022", granularity="monthly")
    assert data_req.requirement == "Get sales data"
    assert data_req.timeframe == "2022"
    assert data_req.granularity == "monthly"

def test_set_fields_invalid():
    data_req = DataRequirements()
    with pytest.raises(ValueError, match="not a valid field of DataRequirements"):
        data_req.set_fields(invalid_field="Invalid")

def test_set_filters_valid():
    data_req = DataRequirements()
    data_req.set_fields(filters={"region": "north", "category": "electronics"})
    assert data_req.filters == {"region": "north", "category": "electronics"}

def test_set_filters_invalid():
    data_req = DataRequirements()
    with pytest.raises(ValueError, match="All keys and values in 'filters' must be strings."):
        data_req.set_fields(filters={"region": 123})

def test_validate_requirements_missing_requirement():
    data_req = DataRequirements()
    with pytest.raises(ValueError, match="Requirement must be specified."):
        data_req.validate_requirements()

def test_validate_requirements_not_gathered():
    data_req = DataRequirements(requirement="Get sales data")
    with pytest.raises(ValueError, match="Requirements must be marked as gathered."):
        data_req.validate_requirements()

def test_set_requirements_gathered():
    data_req = DataRequirements()
    data_req.set_requirements_gathered(True)
    assert data_req.requirements_gathered
    data_req.set_requirements_gathered(False)
    assert not data_req.requirements_gathered

def test_validate_timeframe_invalid_type():
    data_req = DataRequirements(requirement="Get sales data", requirements_gathered=True, timeframe=2022)
    with pytest.raises(ValueError, match="Timeframe must be a string."):
        data_req.validate_requirements()

def test_validate_granularity_invalid_type():
    data_req = DataRequirements(requirement="Get sales data", requirements_gathered=True, granularity=123)
    with pytest.raises(ValueError, match="Granularity must be a string."):
        data_req.validate_requirements()

def test_validate_domain_context_invalid_type():
    data_req = DataRequirements(requirement="Get sales data", requirements_gathered=True, domain_context=123)
    with pytest.raises(ValueError, match="Domain context must be a string."):
        data_req.validate_requirements()