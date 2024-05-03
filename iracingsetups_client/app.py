import asyncio
import logging
import logging.config
import time

import irsdk
import uvloop

from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing.helpers import State, check_iracing


async def startup():
    logging.info("Starting IRacingSetups client - environment %s", environment)

    ir = irsdk.IRSDK()
    logging.info("irsdk initialized")
    state = State()
    max_retries = 5
    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing(state, ir)
            # if we are, then process data
            if state.ir_connected:
                max_retries = 5
                logging.info("Connect to iracing")
            else:
                logging.info("failed to connect to iracing")
                max_retries -= 1
                if max_retries == 0:
                    logging.info("max retries reached, exiting")
                    exit()

            # sleep for 1 second
            # maximum you can use is 1/60
            # cause iracing updates data with 60 fps
            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass


def main():
    logging.config.dictConfig(config)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(startup())


if __name__ == "__main__":
    main()