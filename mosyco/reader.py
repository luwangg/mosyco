"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
from functools import wraps
from helpers import load_dataframe

class Reader:

    # TODO: what server address to use?
    def __init__(self):
        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now pretend that these values come from a system:
        self.dataframe = load_dataframe()

        # TODO: multiple live systems - have a dictionary of systems and
        # feed
        self.systems = {}


    def send_model_data(self, column_name='ProduktA'):
        return self.dataframe.loc[:, column_name]

    # build generator that pops out value for each live system
    def generate_values(self, system_name='PAcombi'):
        series = self.dataframe.loc[:, system_name]
        for entry in series:
            yield entry

# =================================

    def choose_system(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            print 'Calling decorated function'
            return f(*args, **kwds)
        return wrapper

    @choose_system
    def example(self, system):
        """Docstring"""
        print 'Called example function'

# =================================

    class LiveSystem:
        def __init__(self, column_name='PAcombi'):
            self.series =




if __name__ == '__main__':
    reader = Reader()
    reader.run()
