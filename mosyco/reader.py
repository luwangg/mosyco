# -*- coding: utf-8 -*-
"""
The reader module observes an operative system (in real-time) and pushes
observed as well as simulated values to the inspector for analysis.
"""
import logging
import threading
import time
import mosyco.helpers as helpers

log = logging.getLogger(__name__)

class Reader(threading.Thread):
    """The Reader class serves as an interface to system and model components.

    The Reader can read data from multiple running systems as well as model data.
    This data is transferred to the Inspector for further analysis. The Reader is
    run as a separate thread.

    Attributes:
        df (DataFrame): Simulates data sources of running systems and models.
        systems (dict): keys: system names, values: generators for live system data.
        queue (queue): to communicate with the inspector across threads.
    """
    def __init__(self, sources, queue):
        """Return a new Reader object.

        Args:
            sources (str): list of column names for actual value data
        """
        # For now we pretend that these values come from a system:
        super().__init__(daemon=True)
        self.df = helpers.load_dataframe()
        self.queue = queue
        self.systems = sources

        log.info("Initialized reader...")

    def run(self):
        log.debug("Reader.run() called. Starting to send data to queue now...")
        frame = self.df.loc[:, self.systems]
        for entry in frame.itertuples():
            self.queue.put(entry)
            time.sleep(0.01)
        # signal that reader is done
        self.queue.put(None)
        log.debug("The Reader is now idle.")
