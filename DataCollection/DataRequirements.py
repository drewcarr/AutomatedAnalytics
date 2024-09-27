class DataRequirements:
    def __init__(self):
        self.requirements = ""  # String to hold what the user is looking for
        self.requirements_gathered = False  # Boolean to indicate when enough info has been gathered

    def set_requirements(self, requirements: str):
        """ sets the requirements """
        self.requirements = requirements

    def toggle_requirements_gathered(self, status: bool):
        """ Toggles whether all requirements have been gathered """
        self.requirements_gathered = status

    def reset(self):
        """Reset the class for a new session"""
        self.requirements = ""
        self.requirements_gathered = False

