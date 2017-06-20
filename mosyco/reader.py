"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
import logging as log
from functools import wraps
from helpers import load_dataframe

class Reader:
    # default_system is the name of the column of the actual values (IST-Werte)
    def __init__(self, default_system='PAcombi'):
        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now pretend that these values come from a system:
        self.dataframe = load_dataframe()
        self.systems = {}
        self.set_current_system(default_system)
        log.info("Initialized reader...")


    def get_model_data(self, column_name='ProduktA'):
        """Send model data in batch. Returns pandas Series object."""
        return self.dataframe.loc[:, column_name]

    def actual_value_gen(self):
        """Generate actual values from the currently active system. Returns a tuple."""
        yield from self.systems.get(self.current_system)

    def create_generator(self, system='PAcombi'):
        series = self.dataframe.loc[:, system]
        for entry in series.iteritems():
            yield entry

    def set_current_system(self, system):
        """Set the current system."""
        # TODO: assert new system is a column name in DF
        if system not in self.systems:
            gen = self.create_generator(system)
            self.systems[system] = gen
            self.current_system = system
        else:
            self.current_system = system

if __name__ == '__main__':
    reader = Reader()
