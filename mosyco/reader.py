"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
from functools import wraps
from helpers import load_dataframe

class Reader:
    # default_system is the name of the column of the actual values (IST-Werte)
    def __init__(self, default_system='PAcombi'):
        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now pretend that these values come from a system:
        self.dataframe = load_dataframe()
        self.systems = {
            default_system: self.dataframe.loc[:, default_system],
        }

    def send_model_data(self, column_name='ProduktA'):
        """Send model data in Batch. Returns pandas Series object."""
        return self.dataframe.loc[:, column_name]

    def pick_system(fn):
        """Decorate generators to emit actual values lazily."""
        @wraps(fn)
        def wrapper(self, system_name='PAcombi'):
            print("Calling wrapper with {}".format(system_name))
            return fn(self, system_name)
        return wrapper

    @pick_system
    def actual_value_gen(self, system_name='PAcombi'):
        """Generate successive actual values and return them as a Seris object"""
        series = self.dataframe.loc[:, system_name]
        for entry in series:
            yield entry


if __name__ == '__main__':
    reader = Reader()
