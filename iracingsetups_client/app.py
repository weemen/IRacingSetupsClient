import logging
import logging.config
import time
import pprint

import grpc
import irsdk

import iracingsetups_client.iracing_pb2 as iracing_pb2
from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing.helpers import State, check_iracing
from iracingsetups_client.iracing_pb2_grpc import IracingServiceStub

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
    current_info = {
        "telemetry": dict(),
    }
    printed = False

    # TODO: initialization of some variables to minimize networking calls
    # TODO: Figure out if brake bias changes in the car setup when changing bbal during a session
    #  -> only front -> static -> dcBrakeBias
    # TODO: Number of sector times is different per ciruit.
    #  -> len over SplitTimeInfo.Sectors
    # IsOnTrackCar
    # IsInGarage
    event_buffer = []
    track_information_send = False
    driver_information_send = False

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing(state, ir)
            # if we are, then process data
            if state.ir_connected:
                logging.info("Connect to iracing")
                host = "192.168.178.70:9001"
                with grpc.aio.insecure_channel(host) as channel:
                    stub = IracingServiceStub(channel)
                    try:
                        response = stub.SendNewSession(
                            iracing_pb2.SendNewSessionRequest(
                            userId="898674",
                            session_id=ir['WeekendInfo']['SessionID'],
                            track=iracing_pb2.TrackMessage(
                                trackId=ir['WeekendInfo']['TrackID'],
                                name=f"{ir['WeekendInfo']['TrackDisplayName']} ({ir['WeekendInfo']['TrackName']})",
                                configName=ir['WeekendInfo']['TrackConfigName'],
                                city=ir['WeekendInfo']['TrackCity'],
                                country=ir['WeekendInfo']['TrackCountry'],
                                trackGps=iracing_pb2.GPSTrack(
                                    trackGpsLat=ir['WeekendInfo']['TrackLatitude'],
                                    trackGpsLong=ir['WeekendInfo']['TrackLongitude'],
                                    trackGpsAlt=ir['WeekendInfo']['TrackAltitude'],
                                ),
                                length=ir['WeekendInfo']['TrackLength'],
                                turns=ir['WeekendInfo']['TrackNumTurns'],
                            ),
                            driver=iracing_pb2.DriverMessage(
                                driverId=ir['DriverInfo']['Drivers'][0]['UserID'],
                                driverName=ir['DriverInfo']['Drivers'][0]['UserName'],
                                driverCar=ir['DriverInfo']['Drivers'][0]['CarScreenName'],
                                driverCarId=ir['DriverInfo']['Drivers'][0]['CarID'],
                                driverTeamId=ir['DriverInfo']['Drivers'][0]['TeamID'],
                                driverSetupName=ir['DriverInfo']['Drivers'][0]['DriverSetupName'],
                            )
                        ))


                        # car_setup = SendLapRequest.CarSetup(
                        #     chassis=SendLapRequest.Chassis(
                        #         chassisqFront=SendLapRequest.ChassisFront(
                        #             arbBlades=ir['CarSetup']['Chassis']['Front']['ArbBlades'],
                        #             arbDriveArmLength=ir['CarSetup']['Chassis']['Front']['ArbDriveArmLength'],
                        #             arbSize=ir['CarSetup']['Chassis']['Front']['ArbSize'],
                        #             arbPreload=ir['CarSetup']['Chassis']['Front']['ArbPreload'],
                        #             brakePressureBias=ir['CarSetup']['Chassis']['Front']['BrakePressureBias'],
                        #             crossWeight=ir['CarSetup']['Chassis']['Front']['CrossWeight'],
                        #             displayPage=ir['CarSetup']['Chassis']['Front']['DisplayPage'],
                        #             frontMasterCylinder=ir['CarSetup']['Chassis']['Front']['FrontMasterCylinder'],
                        #             heaveDamperDefl=ir['CarSetup']['Chassis']['Front']['HeaveDamperDefl'],
                        #             heavePerchOffset=ir['CarSetup']['Chassis']['Front']['HeavePerchOffset'],
                        #             heaveSpring=ir['CarSetup']['Chassis']['Front']['HeaveSpring'],
                        #             heaveSpringDefl=ir['CarSetup']['Chassis']['Front']['HeaveSpringDefl'],
                        #             pushrodLengthOffset=ir['CarSetup']['Chassis']['Front']['PushrodLengthOffset'],
                        #             rearMasterCylinder=ir['CarSetup']['Chassis']['Front']['RearMasterCylinder'],
                        #         ),
                        #         chassisLeftFront=SendLapRequest.ChassisFrontSide(
                        #             camber=ir['CarSetup']['Chassis']['LeftFront']['Camber'],
                        #             caster=ir['CarSetup']['Chassis']['LeftFront']['Caster'],
                        #             compDamping=ir['CarSetup']['Chassis']['LeftFront']['CompDamping'],
                        #             cornerWeight=ir['CarSetup']['Chassis']['LeftFront']['CornerWeight'],
                        #             rbdDamping=ir['CarSetup']['Chassis']['LeftFront']['RbdDamping'],
                        #             rideHeight=ir['CarSetup']['Chassis']['LeftFront']['RideHeight'],
                        #             shockDefl=ir['CarSetup']['Chassis']['LeftFront']['ShockDefl'],
                        #             springDefl=ir['CarSetup']['Chassis']['LeftFront']['SpringDefl'],
                        #             toeIn=ir['CarSetup']['Chassis']['LeftFront']['ToeIn'],
                        #             torsionBarOD=ir['CarSetup']['Chassis']['LeftFront']['TorsionBarOD'],
                        #             torsionBarPreload=ir['CarSetup']['Chassis']['LeftFront']['TorsionBarPreload'],
                        #         ),
                        #         chassisRightFront=SendLapRequest.ChassisFrontSide(
                        #             camber=ir['CarSetup']['Chassis']['RightFront']['Camber'],
                        #             caster=ir['CarSetup']['Chassis']['RightFront']['Caster'],
                        #             compDamping=ir['CarSetup']['Chassis']['RightFront']['CompDamping'],
                        #             cornerWeight=ir['CarSetup']['Chassis']['RightFront']['CornerWeight'],
                        #             rbdDamping=ir['CarSetup']['Chassis']['RightFront']['RbdDamping'],
                        #             rideHeight=ir['CarSetup']['Chassis']['RightFront']['RideHeight'],
                        #             shockDefl=ir['CarSetup']['Chassis']['RightFront']['ShockDefl'],
                        #             springDefl=ir['CarSetup']['Chassis']['RightFront']['SpringDefl'],
                        #             toeIn=ir['CarSetup']['Chassis']['RightFront']['ToeIn'],
                        #             torsionBarOD=ir['CarSetup']['Chassis']['RightFront']['TorsionBarOD'],
                        #             torsionBarPreload=ir['CarSetup']['Chassis']['RightFront']['TorsionBarPreload'],
                        #         ),
                        #         chassisRear=SendLapRequest.ChassisRear(
                        #             arbDriveArmLength=ir['CarSetup']['Chassis']['Rear']['ArbDriveArmLength'],
                        #             arbSize=ir['CarSetup']['Chassis']['Rear']['ArbSize'],
                        #             brakePressureBias=ir['CarSetup']['Chassis']['Rear']['BrakePressureBias'],
                        #             fuelLevel=ir['CarSetup']['Chassis']['Rear']['FuelLevel'],
                        #             pushrodLengthOffset=ir['CarSetup']['Chassis']['Rear']['PushrodLengthOffset'],
                        #             thirdDamperDefl=ir['CarSetup']['Chassis']['Rear']['ThirdDamperDefl'],
                        #             thirdPerchOffset=ir['CarSetup']['Chassis']['Rear']['ThirdPerchOffset'],
                        #             thirdSpring=ir['CarSetup']['Chassis']['Rear']['ThirdSpring'],
                        #             thirdSpringDefl=ir['CarSetup']['Chassis']['Rear']['ThirdSpringDefl'],
                        #         ),
                        #         chassisLeftRear=SendLapRequest.ChassisRearSide(
                        #             camber=ir['CarSetup']['Chassis']['LeftRear']['Camber'],
                        #             compDamping=ir['CarSetup']['Chassis']['LeftRear']['CompDamping'],
                        #             cornerWeight=ir['CarSetup']['Chassis']['LeftRear']['CornerWeight'],
                        #             cbdDamping=ir['CarSetup']['Chassis']['LeftRear']['CbdDamping'],
                        #             rideHeight=ir['CarSetup']['Chassis']['LeftRear']['RideHeight'],
                        #             shockDefl=ir['CarSetup']['Chassis']['LeftRear']['ShockDefl'],
                        #             springDefl=ir['CarSetup']['Chassis']['LeftRear']['SpringDefl'],
                        #             springRate=ir['CarSetup']['Chassis']['LeftRear']['SpringRate'],
                        #             toeIn=ir['CarSetup']['Chassis']['LeftRear']['ToeIn'],
                        #         ),
                        #         chassisRightRear=SendLapRequest.ChassisRearSide(
                        #             camber=ir['CarSetup']['Chassis']['RightRear']['Camber'],
                        #             compDamping=ir['CarSetup']['Chassis']['RightRear']['CompDamping'],
                        #             cornerWeight=ir['CarSetup']['Chassis']['RightRear']['CornerWeight'],
                        #             cbdDamping=ir['CarSetup']['Chassis']['RightRear']['CbdDamping'],
                        #             rideHeight=ir['CarSetup']['Chassis']['RightRear']['RideHeight'],
                        #             shockDefl=ir['CarSetup']['Chassis']['RightRear']['ShockDefl'],
                        #             springDefl=ir['CarSetup']['Chassis']['RightRear']['SpringDefl'],
                        #             springPerchOffset=ir['CarSetup']['Chassis']['RightRear']['SpringPerchOffset'],
                        #             springRate=ir['CarSetup']['Chassis']['RightRear']['SpringRate'],
                        #             toeIn=ir['CarSetup']['Chassis']['RightRear']['ToeIn'],
                        #         ),
                        #     ),
                        #     drivetrain=SendLapRequest.Drivetrain(
                        #         drivetrainDiff=SendLapRequest.DrivetrainDiff(
                        #             diffClutchFrictionFaces=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffClutchFrictionFaces'],
                        #             diffPreload=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffPreload'],
                        #             diffRampAngles=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffRampAngles'],
                        #         ),
                        #         drivetrainDt=SendLapRequest.DrivetrainDt(
                        #             firstGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FirstGear'],
                        #             secondGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['SecondGear'],
                        #             thirdGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['ThirdGear'],
                        #             fourthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FourthGear'],
                        #             fifthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FifthGear'],
                        #             sixthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['SixthGear'],
                        #         ),
                        #     ),
                        #     tyresAero=SendLapRequest.TyresAero(
                        #         aeroSetup=SendLapRequest.AeroSetup(
                        #             aeroPackage=ir['setup']['TyresAero']['AeroSetup']['AeroPackage'],
                        #             frontFlapAngle=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapAngle'],
                        #             frontFlapConfiguration=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapConfiguration'],
                        #             frontFlapGurneyFlap=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapGurneyFlap'],
                        #             rearBeamWingAngle=ir['CarSetup']['TyresAero']['AeroSetup']['RearBeamWingAngle'],
                        #             rearUpperFlapAngle=ir['CarSetup']['TyresAero']['AeroSetup']['RearUpperFlapAngle'],
                        #         ),
                        #         LeftFront=SendLapRequest.AeroTyre(
                        #             coldPressure=ir['CarSetup']['TyresAero']['LeftFront']['ColdPressure'],
                        #             lastHotPressure=ir['CarSetup']['TyresAero']['LeftFront']['LastHotPressure'],
                        #             lastTempsOMI=ir['CarSetup']['TyresAero']['LeftFront']['LastTempsOMI'],
                        #             treadRemaining=ir['CarSetup']['TyresAero']['LeftFront']['TreadRemaining'],
                        #         ),
                        #         RightFront=SendLapRequest.AeroTyre(
                        #             coldPressure=ir['CarSetup']['TyresAero']['RightFront']['ColdPressure'],
                        #             lastHotPressure=ir['CarSetup']['TyresAero']['RightFront']['LastHotPressure'],
                        #             lastTempsOMI=ir['CarSetup']['TyresAero']['RightFront']['LastTempsOMI'],
                        #             treadRemaining=ir['CarSetup']['TyresAero']['RightFront']['TreadRemaining'],
                        #         ),
                        #         LeftRear=SendLapRequest.AeroTyre(
                        #             coldPressure=ir['CarSetup']['TyresAero']['LeftRear']['ColdPressure'],
                        #             lastHotPressure=ir['CarSetup']['TyresAero']['LeftRear']['LastHotPressure'],
                        #             lastTempsOMI=ir['CarSetup']['TyresAero']['LeftRear']['LastTempsOMI'],
                        #             treadRemaining=ir['CarSetup']['TyresAero']['LeftRear']['TreadRemaining'],
                        #         ),
                        #         RightRear=SendLapRequest.AeroTyre(
                        #             coldPressure=ir['CarSetup']['TyresAero']['RightRear']['ColdPressure'],
                        #             lastHotPressure=ir['CarSetup']['TyresAero']['RightRear']['LastHotPressure'],
                        #             lastTempsOMI=ir['CarSetup']['TyresAero']['RightRear']['LastTempsOMI'],
                        #             treadRemaining=ir['CarSetup']['TyresAero']['RightRear']['TreadRemaining'],
                        #         )
                        #     )
                        # )
                        #
                        # split_time_info = SendLapRequest.SplitTimeInfo(
                        #     sectors=[
                        #         SendLapRequest.Sector(
                        #             sectorNum=1,
                        #             sectorStartPct=0.25,
                        #         ),
                        #         SendLapRequest.Sector(
                        #             sectorNum=2,
                        #             sectorStartPct=0.5,
                        #         ),
                        #         SendLapRequest.Sector(
                        #             sectorNum=3,
                        #             sectorStartPct=0.75,
                        #         ),
                        #     ]
                        # )
                        #
                        # telemetry = SendLapRequest.Telemetry(
                        #     lap=ir['Lap'],
                        #     lapCompleted=ir['LapCompleted'],
                        #     lapCurrentLapTime=ir['LapCurrentLapTime'],
                        #     lapDeltaToBestLap=ir['LapDeltaToBestLap'],
                        #     lapDist=ir['LapDist'],
                        #     lapDistPct=ir['LapDistPct'],
                        #     lapLastLapTime=ir['LapLastLapTime'],
                        #     playerCarMyIncidentCount=ir['PlayerCarMyIncidentCount'],
                        #     playerCarTeamIncidentCount=ir['PlayerCarTeamIncidentCount'],
                        # )
                        #
                        # grpc_request = SendLapRequest(
                        #     userId="898674",
                        #     session_id=ir['sessionuniqueid'],
                        #     track=track,
                        #     driver=driver,
                        #     carSetup=car_setup,
                        #     splitTimeInfo=split_time_info,
                        #     telemetry=telemetry,
                        # )
                    except grpc.aio.AioRpcError as e:
                        logging.error("Error data not send to server: %s", e)
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