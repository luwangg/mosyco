#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from mosyco import Mosyco
from mosyco import parser
from mosyco import helpers

def main():
    # read command line arguments & set log level
    args = parser.parse_arguments()
    log = helpers.setup_logging(args)

    log.info('Starting mosyco...')
    log.debug('Running in DEBUG Mode')

    # Run Mosyco
    try:
        app = Mosyco(args)
        app.run()
    except KeyboardInterrupt:
        log.info(' Interrupted. Exiting now...')
        sys.exit()
    except:
        raise


if __name__ == '__main__':
    main()
