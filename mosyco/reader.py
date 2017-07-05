# -*- coding: utf-8 -*-
"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
import logging
import mosyco.helpers as helpers

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Reader:
    # default_system is the name of the column of the actual values (IST-Werte)
    def __init__(self, default_system='PAcombi'):
        # TODO: Schnittstelle 1 zu operativen Systemen und zu "Model"
        # For now pretend that these values come from a system:
        self.df = helpers.load_dataframe()
        self.systems = {}
        self.set_current_system(default_system)
        log.info("Initialized reader...")

    def actual_value_gen(self):
        """Generate actual values from the currently active system. Returns a tuple."""
        yield from self.systems.get(self.current_system)

    def _create_generator(self, system='PAcombi'):
        """Create a generator object for system to quickly & lazily access dataframe columns"""
        # square brackets around system to get DataFrame instead of Series object
        series = self.df.loc[:, [system]]
        for entry in series.itertuples():
            yield entry

    def set_current_system(self, system):
        """Set the current system."""
        assert system in self.df.columns
        if system not in self.systems:
            gen = self._create_generator(system)
            self.systems[system] = gen
            self.current_system = system
        else:
            self.current_system = system
