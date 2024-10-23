from typing import List
from DataCollection.LocalDatasetAgent import DatasetCoverage
from common.DataRequirements import DataRequirements
from common.Orchestrators.BaseTeamState import BaseTeamState


class DataCollectionTeamState(BaseTeamState):
    """
    Extended state for the DataCollectionTeam.
    messages: Annotated[List[BaseMessage], add]
    validated: bool
    next: str
    Error: str
    """
    data_requirements: DataRequirements
    dataset_coverages: List[DatasetCoverage]