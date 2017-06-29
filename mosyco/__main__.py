# -*- coding: utf-8 -*-
import asyncio
import logging

from mosyco.inspector import Inspector
from mosyco.reader import Reader

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# loop = asyncio.get_event_loop()

def main():
    log.info('Starting mosyco...')

    reader = Reader()
    inspector = Inspector(reader.df.index, reader.df.PAmodel)

    iterations = 0

    for val in reader.actual_value_gen():
        log.debug(val[0])
        inspector.receive_actual_value(val)
        if val[0].month == 12 and val[0].day == 31:
            log.debug('a year has passed')



        asyncio.sleep(0.5)
        iterations += 1
        # if iterations > 5:
        #     break


    log.info('...finished!')

if __name__ == '__main__':
    main()
