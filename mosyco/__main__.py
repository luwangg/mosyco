# -*- coding: utf-8 -*-

import pandas as pd

# import asyncio
# import time
import logging

from mosyco.inspector import Inspector
from mosyco.reader import Reader

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# loop = asyncio.get_event_loop()

def main():
    log.info('Starting mosyco...')

    # initialize reader and inspector
    reader = Reader()
    # TODO: remove PAmodel hard-coded ref
    inspector = Inspector(reader.df.index, reader.df.PAmodel)

    # the actual value generator simulates incoming data from a monitored system.
    # the reader reads this data and sends it to the inspector

    count = 0

    # main loop starts here:
    for (date, value) in reader.actual_value_gen():
        # send value to inspector
        inspector.receive_actual_value((date, value))

        log.debug(date.date())


        # create a forecast every year and eval model based on it
        if date.month == 12 and date.day == 31:
            next_year = date.year + 1

            log.info(f'current date: {date.date()} / value: {value:.2f}')

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


        (exceeds_threshold, deviation) = inspector.eval_actual(date)
        if exceeds_threshold:
            count += 1

        # asyncio.sleep(0.5)
        # time.sleep(0.1)

    log.info('...finished!')
    log.info(f'Total: {count} deviations deteced.')

if __name__ == '__main__':
    main()
