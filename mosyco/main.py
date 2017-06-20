# import asyncio
import logging as log

from inspector import Inspector
from reader import Reader


# loop = asyncio.get_event_loop()

def main():
    log.basicConfig(level=log.INFO)
    log.info('Starting mosyco...')
    inspector = Inspector()
    inspector.dummy()
    reader = Reader()

    for entry in reader.actual_value_gen():
        log.info(entry)
        break

if __name__ == '__main__':
    main()
