# -*- coding: utf-8 -*-

import pandas as pd
import logging

from mosyco.inspector import Inspector
from mosyco.reader import Reader
import mosyco.parser

log = logging.getLogger(__name__)

# read command line arguments & set log level
args = mosyco.parser.parse_arguments()
log.setLevel(args.loglevel)

# ==============================================================================
log.info('Starting mosyco...')
log.debug('running in DEBUG Mode')
# initialize reader and inspector
reader = Reader(args.system)
inspector = Inspector(reader.df.index, reader.df[args.model])

# the actual value generator simulates incoming data from a monitored system.
# the reader reads this data and sends it to the inspector

deviation_count = 0

# ==============================================================================
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
            period = pd.Period(next_year)
            log.info(f'Generating forecast for {period}...')
            inspector.forecast_year(period, args.system)
            # forecast number is now in inspector.forecast dataframe

            # errors is a dataframe of the year with NaN values where the
            # model data falls outside the forecast confidence interval
            # TODO: could be used for plotting
            # errors = inspector.eval_future(next_year)
            inspector.eval_future(period)


    (exceeds_threshold, deviation) = inspector.eval_actual(date, args.system)
    if exceeds_threshold:
        deviation_count += 1

log.info(f'Total: {deviation_count} model-actual deviations detected.')
log.info('...finished!')
# ==============================================================================
