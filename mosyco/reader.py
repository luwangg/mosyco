# -*- coding: utf-8 -*-
"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
import logging
import mosyco.helpers as helpers

log = logging.getLogger(__name__)

class Reader:
    """The Reader class serves as an interface to system and model components.

    The Reader can read data from multiple running systems as well as model data.
    This data can then be transferred to the Inspector for further analysis.

    Attributes:
        df (DataFrame): Simulates data sources of running systems and models.
        systems (dict): keys: system names, values: generators for live system data.
        current_system (str): Name of the currently active system. e.g. 'PAcombi'.
    """
    def __init__(self, actual_value_source):
        """Return a new Reader object.

        Args:
            actual_value_source (str): column name for actual value data
        """
        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now we pretend that these values come from a system:
        self.df = helpers.load_dataframe()
        self.systems = {}
        self.current_system = None
        self.set_current_system(actual_value_source)
        log.info("Initialized reader...")

    def actual_value_gen(self):
        """Generate actual values from the currently active system."""
        yield from self.systems.get(self.current_system)

    def _create_generator(self):
        """Create generator object for system to quickly access dataframe columns."""
        # square brackets around system to get DataFrame instead of Series object
        series = self.df.loc[:, [self.current_system]]
        for entry in series.itertuples():
            yield entry

    def set_current_system(self, system):
        """Set the current system."""
        assert system in self.df.columns
        if system not in self.systems:
            self.current_system = system
            gen = self._create_generator()
            self.systems[system] = gen
        else:
            self.current_system = system
