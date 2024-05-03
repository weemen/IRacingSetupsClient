import logging
import logging.config
import time

import irsdk

from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing.helpers import State, check_iracing


def startup():
    logging.info("Starting IRacingSetups client - environment %s", environment)

    ir = irsdk.IRSDK()
    logging.info("irsdk initialized")
    state = State()
    current_info = {}
    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing(state, ir)
            # if we are, then process data
            if state.ir_connected:
                logging.info("Connect to iracing")
                current_info["track"] = {
                    "id": ir['WeekendInfo']['TrackID'],
                    "name": ir['WeekendInfo']['TrackName'],
                    "configName": ir['WeekendInfo']['TrackConfigName'],
                }
                logging.info(ir["SessionInfo"])
            else:
                logging.info("failed to connect to iracing")

            # sleep for 1 second
            # maximum you can use is 1/60
            # cause iracing updates data with 60 fps
            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass


def main():
    logging.config.dictConfig(config)
    startup()


if __name__ == "__main__":
    main()