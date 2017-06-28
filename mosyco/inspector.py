# -*- coding: utf-8 -*-
import pandas as pd
import logging

import mosyco.methods as methods

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Inspector:
    def __init__(self, index, column):
        # The index should be the reader's index. This means that the reader and
        # inspector dataframes will share the same index object.
        # columns should be the model data that is passed in batch.
        self.df = pd.DataFrame(data=column.copy(), index=index)

    def receive_actual_value(self, val, system='PAcombi'):
        """Fills inspector dataframe with actual values."""
        # val is a tuple of (index, value)
        self.df.set_value(val[0], system, val[1])

    def evaluate(self, date):
        """Evaluate the deviation between Model and Actual for given date.
        Return the deviation if it exceeds a threshold or False if not."""
        # TODO: THRESHOLD, rm hardcoded variables
        # col is the name of the column we want
        actual_column = 'PAcombi'
        model_column = 'ProduktA'

        actual = self.df.loc[date, actual_column]
        model = self.df.loc[date, model_column]

        threshold = 0.2

        return methods.relative_deviation(model, actual, threshold)




if __name__ == '__main__':
    pass
