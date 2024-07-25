import logging
import logging.config
import time
import pprint

import irsdk

from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing.helpers import State, check_iracing

# set up pretty printer
pp = pprint.PrettyPrinter(indent=2, sort_dicts=True)


def log_pretty(obj):
    pretty_out = f"{pp.pformat(obj)}"

    return f'{pretty_out}\n'


def startup():
    logging.info("Starting IRacingSetups client - environment %s", environment)

    ir = irsdk.IRSDK()
    logging.info("irsdk initialized")
    state = State()
    current_info = {}
    printed = False
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
                    "name": f"{ir['WeekendInfo']['TrackDisplayName']} ({ir['WeekendInfo']['TrackName']})",
                    "configName": ir['WeekendInfo']['TrackConfigName'],
                    "city": ir['WeekendInfo']['TrackCity'],
                    "country": ir['WeekendInfo']['TrackCountry'],
                    "gps": {
                        "latitude": ir['WeekendInfo']['TrackLatitude'],
                        "longitude": ir['WeekendInfo']['TrackLongitude'],
                        "altitude": ir['WeekendInfo']['TrackAltitude'],
                    },
                    "length": ir['WeekendInfo']['TrackLength'],
                    "turns": ir['WeekendInfo']['TrackNumTurns'],
                }

                # current_info["session"] = {
                #     "fastedLapTime": ir['SessionInfo']['SessionLaps'][0]['Results'][0]['FastestTime'],
                #     "laps": ir['SessionInfo']['Sessions'][0]['Results'][0]['Laps'],
                # }

                myUserId = "898674"
                for driver in ir['DriverInfo']['Drivers']:
                    if driver['UserID'] == myUserId:
                        current_info["driver"] = {
                            "id": driver['UserID'],
                            "name": driver['UserName'],
                            "car": driver['CarScreenName'],
                            "carId": driver['CarID'],
                            "teamId": driver['TeamID'],
                            "setup": driver['DriverSetupName'],
                        }
                        break

                current_info["setup"] = ir['CarSetup']
                current_info["telemetry"] = ir['Telemetry']["Lap"]
                current_info["telemetry"] = ir['Telemetry']["LapCompleted"]
                current_info["telemetry"] = ir['Telemetry']["LapLastLapTime"]

                current_info["telemetry"] = ir['Telemetry']["LapCurrentLapTime"]
                current_info["telemetry"] = ir['Telemetry']["LapDeltaToBestLap"]
                current_info["telemetry"] = ir['Telemetry']["LapDist"]
                current_info["telemetry"] = ir['Telemetry']["LapDistPct"]

                current_info["telemetry"] = ir['Telemetry']["PlayerCarMyIncidentCount"]
                current_info["telemetry"] = ir['Telemetry']["PlayerCarTeamIncidentCount"]
                # telemetry data
                # logging.info(ir['Telemetry']["Lap"])
                # logging.info(ir['Telemetry']["LapCompleted"])
                # logging.info(ir['Telemetry']["LapLastLapTime"])

                # logging.info(ir['Telemetry']["LapCurrentLapTime"])
                # logging.info(ir['Telemetry']["LapDeltaToBestLap"])
                # logging.info(ir['Telemetry']["LapDist"])
                # logging.info(ir['Telemetry']["LapDistPct"])

                # logging.info(ir['Telemetry']["PlayerCarMyIncidentCount"])
                # logging.info(ir['Telemetry']["PlayerCarTeamIncidentCount"])
                if not printed:
                    logging.info(log_pretty(current_info))
                    printed = True
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