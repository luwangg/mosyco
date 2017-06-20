# import asyncio
import logging

from inspector import Inspector
from reader import Reader


# loop = asyncio.get_event_loop()

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting mosyco...')
    inspector = Inspector()
    inspector.dummy()
    reader = Reader()

    for entry in reader.actual_value_gen():
        logging.info(entry)
        break

if __name__ == '__main__':
    main()
