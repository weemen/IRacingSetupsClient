import logging
import logging.config
import time
import pprint

import grpc
import irsdk

from iracingsetups_client.iracing_pb2 import SendLapRequest
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
    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing(state, ir)
            # if we are, then process data
            if state.ir_connected:
                logging.info("Connect to iracing")
                host = "localhost:50051"
                async with grpc.aio.insecure_channel(host) as channel:
                    stub = IracingServiceStub(channel)

                    track = SendLapRequest.TrackMessage(
                        id=ir['WeekendInfo']['TrackID'],
                        name=f"{ir['WeekendInfo']['TrackDisplayName']} ({ir['WeekendInfo']['TrackName']})",
                        configName=ir['WeekendInfo']['TrackConfigName'],
                        city=ir['WeekendInfo']['TrackCity'],
                        country=ir['WeekendInfo']['TrackCountry'],
                        trackGps=SendLapRequest.GPSTrack(
                            trackGpsLat=ir['WeekendInfo']['TrackLatitude'],
                            trackGpsLong=ir['WeekendInfo']['TrackLongitude'],
                            trackGpsAlt=ir['WeekendInfo']['TrackAltitude'],
                        ),
                        length=ir['WeekendInfo']['TrackLength'],
                        turns=ir['WeekendInfo']['TrackNumTurns'],
                    )

                    driver = SendLapRequest.DriveMessage(
                        driverId=ir['DriverInfo']['Drivers'][0]['UserID'],
                        driverName=ir['DriverInfo']['Drivers'][0]['UserName'],
                        driverCar=ir['DriverInfo']['Drivers'][0]['CarScreenName'],
                        driverCarId=ir['DriverInfo']['Drivers'][0]['CarID'],
                        driverTeamId=ir['DriverInfo']['Drivers'][0]['TeamID'],
                        driverSetupName=ir['DriverInfo']['Drivers'][0]['DriverSetupName'],
                    )

                    car_setup = SendLapRequest.CarSetup(
                        chassis=SendLapRequest.Chassis(
                            chassisqFront=SendLapRequest.ChassisFront(
                                arbBlades=ir['CarSetup']['Chassis']['ChassisFront']['ArbBlades'],
                                arbDriveArmLength=ir['CarSetup']['Chassis']['ChassisFront']['ArbDriveArmLength'],
                                arbSize=ir['CarSetup']['Chassis']['ChassisFront']['ArbSize'],
                                arbPreload=ir['CarSetup']['Chassis']['ChassisFront']['ArbPreload'],
                                crossWeight=ir['CarSetup']['Chassis']['ChassisFront']['CrossWeight'],
                                displayPage=ir['CarSetup']['Chassis']['ChassisFront']['DisplayPage'],
                                frontMasterCylinder=ir['CarSetup']['Chassis']['ChassisFront']['FrontMasterCylinder'],
                                heaveDamperDefl=ir['CarSetup']['Chassis']['ChassisFront']['HeaveDamperDefl'],
                                heavePerchOffset=ir['CarSetup']['Chassis']['ChassisFront']['HeavePerchOffset'],
                                heaveSpring=ir['CarSetup']['Chassis']['ChassisFront']['HeaveSpring'],
                                heaveSpringDefl=ir['CarSetup']['Chassis']['ChassisFront']['HeaveSpringDefl'],
                                pushrodLengthOffset=ir['CarSetup']['Chassis']['ChassisFront']['PushrodLengthOffset'],
                                rearMasterCylinder=ir['CarSetup']['Chassis']['ChassisFront']['RearMasterCylinder'],
                            ),
                            chassisLeftFront=SendLapRequest.ChassisFrontSide(
                                camber=ir['CarSetup']['Chassis']['ChassisLeftFront']['Camber'],
                                caster=ir['CarSetup']['Chassis']['ChassisLeftFront']['Caster'],
                                compDamping=ir['CarSetup']['Chassis']['ChassisLeftFront']['CompDamping'],
                                cornerWeight=ir['CarSetup']['Chassis']['ChassisLeftFront']['CornerWeight'],
                                rbdDamping=ir['CarSetup']['Chassis']['ChassisLeftFront']['RbdDamping'],
                                rideHeight=ir['CarSetup']['Chassis']['ChassisLeftFront']['RideHeight'],
                                shockDefl=ir['CarSetup']['Chassis']['ChassisLeftFront']['ShockDefl'],
                                springDefl=ir['CarSetup']['Chassis']['ChassisLeftFront']['SpringDefl'],
                                toeIn=ir['CarSetup']['Chassis']['ChassisLeftFront']['ToeIn'],
                                torsionBarOD=ir['CarSetup']['Chassis']['ChassisLeftFront']['TorsionBarOD'],
                                torsionBarPreload=ir['CarSetup']['Chassis']['ChassisLeftFront']['TorsionBarPreload'],
                            ),
                            chassisRightFront=SendLapRequest.ChassisFrontSide(
                                camber=ir['CarSetup']['Chassis']['ChassisRightFront']['Camber'],
                                caster=ir['CarSetup']['Chassis']['ChassisRightFront']['Caster'],
                                compDamping=ir['CarSetup']['Chassis']['ChassisRightFront']['CompDamping'],
                                cornerWeight=ir['CarSetup']['Chassis']['ChassisRightFront']['CornerWeight'],
                                rbdDamping=ir['CarSetup']['Chassis']['ChassisRightFront']['RbdDamping'],
                                rideHeight=ir['CarSetup']['Chassis']['ChassisRightFront']['RideHeight'],
                                shockDefl=ir['CarSetup']['Chassis']['ChassisRightFront']['ShockDefl'],
                                springDefl=ir['CarSetup']['Chassis']['ChassisRightFront']['SpringDefl'],
                                toeIn=ir['CarSetup']['Chassis']['ChassisRightFront']['ToeIn'],
                                torsionBarOD=ir['CarSetup']['Chassis']['ChassisRightFront']['TorsionBarOD'],
                                torsionBarPreload=ir['CarSetup']['Chassis']['ChassisRightFront']['TorsionBarPreload'],
                            ),
                            chassisRear=SendLapRequest.ChassisRear(
                                arbDriveArmLength=ir['CarSetup']['Chassis']['ChassisRear']['ArbDriveArmLength'],
                                arbSize=ir['CarSetup']['Chassis']['ChassisRear']['ArbSize'],
                                fuelLevel=ir['CarSetup']['Chassis']['ChassisRear']['FuelLevel'],
                                pushrodLengthOffset=ir['CarSetup']['Chassis']['ChassisRear']['PushrodLengthOffset'],
                                thirdDamperDefl=ir['CarSetup']['Chassis']['ChassisRear']['ThirdDamperDefl'],
                                thirdPerchOffset=ir['CarSetup']['Chassis']['ChassisRear']['ThirdPerchOffset'],
                                thirdSpring=ir['CarSetup']['Chassis']['ChassisRear']['ThirdSpring'],
                                thirdSpringDefl=ir['CarSetup']['Chassis']['ChassisRear']['ThirdSpringDefl'],
                            ),
                            chassisLeftRear=SendLapRequest.ChassisRearSide(
                                camber=ir['CarSetup']['Chassis']['ChassisLeftRear']['Camber'],
                                compDamping=ir['CarSetup']['Chassis']['ChassisLeftRear']['CompDamping'],
                                cornerWeight=ir['CarSetup']['Chassis']['ChassisLeftRear']['CornerWeight'],
                                cbdDamping=ir['CarSetup']['Chassis']['ChassisLeftRear']['CbdDamping'],
                                rideHeight=ir['CarSetup']['Chassis']['ChassisLeftRear']['RideHeight'],
                                shockDefl=ir['CarSetup']['Chassis']['ChassisLeftRear']['ShockDefl'],
                                springDefl=ir['CarSetup']['Chassis']['ChassisLeftRear']['SpringDefl'],
                                springRate=ir['CarSetup']['Chassis']['ChassisLeftRear']['SpringRate'],
                                toeIn=ir['CarSetup']['Chassis']['ChassisLeftRear']['ToeIn'],
                            ),
                            chassisRightRear=SendLapRequest.ChassisRearSide(
                                camber=ir['CarSetup']['Chassis']['ChassisRightRear']['Camber'],
                                compDamping=ir['CarSetup']['Chassis']['ChassisRightRear']['CompDamping'],
                                cornerWeight=ir['CarSetup']['Chassis']['ChassisRightRear']['CornerWeight'],
                                cbdDamping=ir['CarSetup']['Chassis']['ChassisRightRear']['CbdDamping'],
                                rideHeight=ir['CarSetup']['Chassis']['ChassisRightRear']['RideHeight'],
                                shockDefl=ir['CarSetup']['Chassis']['ChassisRightRear']['ShockDefl'],
                                springDefl=ir['CarSetup']['Chassis']['ChassisRightRear']['SpringDefl'],
                                springPerchOffset=ir['CarSetup']['Chassis']['ChassisRightRear']['SpringPerchOffset'],
                                springRate=ir['CarSetup']['Chassis']['ChassisRightRear']['SpringRate'],
                                toeIn=ir['CarSetup']['Chassis']['ChassisRightRear']['ToeIn'],
                            ),
                        ),
                        drivetrain=SendLapRequest.Drivetrain(
                            drivetrainDiff=SendLapRequest.DrivetrainDiff(
                                diffClutchFrictionFaces=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffClutchFrictionFaces'],
                                diffPreload=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffPreload'],
                                diffRampAngles=ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffRampAngles'],
                            ),
                            drivetrainDt=SendLapRequest.DrivetrainDt(
                                firstGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FirstGear'],
                                secondGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['SecondGear'],
                                thirdGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['ThirdGear'],
                                fourthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FourthGear'],
                                fifthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['FifthGear'],
                                sixthGear=ir['CarSetup']['Drivetrain']['DrivetrainDt']['SixthGear'],
                            ),
                        ),
                        tyresAero=SendLapRequest.TyresAero(
                            aeroSetup=SendLapRequest.AeroSetup(
                                aeroPackage=ir['CarSetup']['TyresAero']['AeroSetup']['AeroPackage'],
                                frontFlapAngle=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapAngle'],
                                frontFlapConfiguration=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapConfiguration'],
                                frontFlapGurneyFlap=ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapGurneyFlap'],
                                rearBeamWingAngle=ir['CarSetup']['TyresAero']['AeroSetup']['RearBeamWingAngle'],
                                rearUpperFlapAngle=ir['CarSetup']['TyresAero']['AeroSetup']['RearUpperFlapAngle'],
                            ),
                            aeroTyreLeftFront=SendLapRequest.AeroTyre(
                                coldPressure=ir['CarSetup']['TyresAero']['AeroTyreLeftFront']['ColdPressure'],
                                lastHotPressure=ir['CarSetup']['TyresAero']['AeroTyreLeftFront']['LastHotPressure'],
                                lastTempsOMI=ir['CarSetup']['TyresAero']['AeroTyreLeftFront']['LastTempsOMI'],
                                treadRemaining=ir['CarSetup']['TyresAero']['AeroTyreLeftFront']['TreadRemaining'],
                            ),
                            aeroTyreRightFront=SendLapRequest.AeroTyre(
                                coldPressure=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['ColdPressure'],
                                lastHotPressure=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['LastHotPressure'],
                                lastTempsOMI=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['LastTempsOMI'],
                                treadRemaining=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['TreadRemaining'],
                            ),
                            aeroTyreLeftRear=SendLapRequest.AeroTyre(
                                coldPressure=ir['CarSetup']['TyresAero']['AeroTyreLeftRear']['ColdPressure'],
                                lastHotPressure=ir['CarSetup']['TyresAero']['AeroTyreLeftRear']['LastHotPressure'],
                                lastTempsOMI=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['LastTempsOMI'],
                                treadRemaining=ir['CarSetup']['TyresAero']['AeroTyreRightFront']['TreadRemaining'],
                            )
                        )
                    )

                    split_time_info = SendLapRequest.SplitTimeInfo(
                        sectors=[
                            SendLapRequest.Sector(
                                sectorNum=1,
                                sectorStartPct=0.25,
                            ),
                            SendLapRequest.Sector(
                                sectorNum=2,
                                sectorStartPct=0.5,
                            ),
                            SendLapRequest.Sector(
                                sectorNum=3,
                                sectorStartPct=0.75,
                            ),
                        ]
                    )

                    telemetry = SendLapRequest.Telemetry(
                        lap=ir['Lap'],
                        lapCompleted=ir['LapCompleted'],
                        lapCurrentLapTime=ir['LapCurrentLapTime'],
                        lapDeltaToBestLap=ir['LapDeltaToBestLap'],
                        lapDist=ir['LapDist'],
                        lapDistPct=ir['LapDistPct'],
                        lapLastLapTime=ir['LapLastLapTime'],
                        playerCarMyIncidentCount=ir['PlayerCarMyIncidentCount'],
                        playerCarTeamIncidentCount=ir['PlayerCarTeamIncidentCount'],
                    )

                    grpc_request = SendLapRequest(
                        userId="898674",
                        track=track,
                        driver=driver,
                        carSetup=car_setup,
                        splitTimeInfo=split_time_info,
                        telemetry=telemetry,
                    )

                    logging.info("Sending lap data to server")
                    try:
                        response = stub.SendLap(grpc_request)
                        logging.info("Response: %s", response)
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