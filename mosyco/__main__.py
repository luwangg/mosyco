# -*- coding: utf-8 -*-

import pandas as pd
import logging

from mosyco.inspector import Inspector
from mosyco.reader import Reader

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# ========================================================================
# TODO: read params from command
model_name = 'PAmodel'
actual_name = 'PAcombi'
# ========================================================================

def main():
    log.info('Starting mosyco...')

    # initialize reader and inspector
    reader = Reader(actual_name)
    # TODO: remove PAmodel hard-coded ref
    inspector = Inspector(reader.df.index, reader.df[model_name])

    # the actual value generator simulates incoming data from a monitored system.
    # the reader reads this data and sends it to the inspector

    deviation_count = 0

    # main loop starts here:
    for (date, value) in reader.actual_value_gen():
        # send value to inspector
        inspector.receive_actual_value((date, value), reader.current_system)

        # create a forecast every year and eval model based on it
        if date.month == 12 and date.day == 31:
            next_year = date.year + 1

            log.info(f'current date: {date.date()}')

            # model data ends July 2015 so we don't need a forecast for that year
            if not next_year == 2015:
                # generate the new forecast
                log.info(f'Generating forecast for {next_year}...')
                inspector.forecast_year(pd.Period(next_year))
                # forecast number is now in inspector.forecast dataframe

                # errors is a dataframe of the year with NaN values where the
                # model data falls outside the forecast confidence interval
                # TODO: could be used for plotting
                # errors = inspector.eval_future(next_year)
                inspector.eval_future(next_year)


        (exceeds_threshold, deviation) = inspector.eval_actual(date, actual_name)
        if exceeds_threshold:
            deviation_count += 1

    log.info(f'Total: {deviation_count} deviations detected.')
    log.info('...finished!')

if __name__ == '__main__':
    main()
