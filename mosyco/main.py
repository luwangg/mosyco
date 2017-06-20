import asyncio

from inspector import Inspector
from reader import Reader


loop = asyncio.get_event_loop()


if __name__ == '__main__':
    inspector = Inspector()
    inspector.run()

    reader = Reader()
    reader.run()
