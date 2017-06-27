# import asyncio

from mosyco.inspector import Inspector
from mosyco.reader import Reader

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# loop = asyncio.get_event_loop()

def main():
    log.info('Starting mosyco...')

    inspector = Inspector()
    inspector.dummy()
    reader = Reader()

    for val in reader.actual_value_gen():
        log.debug(val)
        inspector.receive_actual_value(val)
        break

    log.info('...finished!')

if __name__ == '__main__':
    main()
