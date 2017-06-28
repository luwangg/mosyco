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
    inspector = Inspector(reader.df.index, reader.df.ProduktA)

    for val in reader.actual_value_gen():
        log.info(val)
        inspector.receive_actual_value(val)
        asyncio.sleep(0.5)

    log.info('...finished!')

if __name__ == '__main__':
    main()
