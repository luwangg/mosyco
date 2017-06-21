import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Inspector:
    def __init__(self, index):
        # Will share DateTimeIndex object with reader!
        self.df = pd.DataFrame(index=index)

    def receive_actual_value(self, val, system='PAcombi'):
        """Fills inspector dataframe with actual values."""
        # val is a tuple of (index, value)
        self.df.set_value(val[0], system, val[1])
        # if system not in self.df.columns:

        #     log.info("Adding new column: data: {}, date: {}".format(val[1], val[0]))
        #     self.df[system] = pd.Series(data=val, name=system)
        # else:
        #     self.df[system].append(val)

if __name__ == '__main__':
    pass
