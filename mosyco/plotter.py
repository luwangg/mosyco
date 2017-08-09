# -*- coding: utf-8 -*-
import pandas as pd
import logging

import asyncio

from mosyco.animate import AnimatedPlot
from mosyco.inspector import Inspector
from mosyco.reader import Reader
import mosyco.parser

log = logging.getLogger(__name__)


# ==============================================================================
# read command line arguments & set log level
args = mosyco.parser.parse_arguments()
log.setLevel(args.loglevel)

loop = asyncio.get_event_loop()

# initialize reader and inspector
reader = Reader(args.system)
inspector = Inspector(reader.df.index, reader.df[args.model])

ani_plot = AnimatedPlot(inspector, args.system)


# ==============================================================================
# main loop starts here:
for (i, (date, value)) in enumerate(reader.actual_value_gen()):
    # send value to inspector
    inspector.receive_actual_value((date, value), reader.current_system)

    ani_plot.show()

    # ======================================================================
    # REMOVE THIS
    if inspector.df[args.system].count() == 1:
        log.info("inspector is now ready for plotting actual values")
    # ======================================================================


    # create a forecast every year and eval model based on it
    if date.month == 12 and date.day == 31:
        next_year = date.year + 1

        # ======================================================================
        # REMOVE THIS
        if next_year == 2000:
            break
        # ======================================================================

        log.info(f'current date: {date.date()}')

        # model data ends July 2015 so we don't need a forecast for that year
        if not next_year == 2015:
            # generate the new forecast
            log.info(f'Generating forecast for {next_year}...')
            inspector.forecast_period(pd.Period(next_year), args.system)
            # forecast number is now in inspector.forecast dataframe

            # errors is a dataframe of the year with NaN values where the
            # model data falls outside the forecast confidence interval
            # TODO: could be used for plotting
            # errors = inspector.eval_future(next_year)
            inspector.eval_future(next_year)


    (exceeds_threshold, deviation) = inspector.eval_actual(date, args.system)
# ==============================================================================
