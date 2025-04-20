import logging
import logging.config
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import grpc
import irsdk

import iracingsetups_client.iracing_pb2 as iracing_pb2
from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing_pb2_grpc import IracingServiceStub


@dataclass
class SessionState:
    """Tracks the state of the current iRacing session"""
    is_connected = False
    is_registered: bool = False
    car_setup_sent: bool = False
    is_on_track: bool = False
    outlap_completed: bool = False
    last_sector: int = 0
    current_lap: int = 0
    session_id: str = ""  # Store the UUID for the current session


class IRacingClient:
    def __init__(self, host: str = "192.168.178.104:9001"):
        self.host = host
        self.ir = irsdk.IRSDK()
        self.state = SessionState()
        self.channel = None
        self.stub = None

    def connect_to_grpc(self):
        """Establishes gRPC connection"""
        if not self.channel:
            self.channel = grpc.insecure_channel(self.host, compression=grpc.Compression.Gzip)
            self.stub = IracingServiceStub(self.channel)

    def disconnect_from_grpc(self):
        """Closes gRPC connection"""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None

    def register_session(self) -> bool:
        """Registers a new session with the server"""
        if not self.state.is_connected:
            return False
        logging.info("Connection to iRacing established")
        try:
            # Generate a new UUID for this session
            self.state.session_id = str(uuid.uuid4())
            # Create session request
            request = iracing_pb2.SendNewSessionRequest(
                userId="898674",  # TODO: Make this configurable
                sessionId=self.state.session_id,
                track=iracing_pb2.TrackMessage(
                    trackId=str(self.ir['WeekendInfo']['TrackID']).encode('utf-8'),
                    name=self.ir['WeekendInfo']['TrackDisplayName'].encode('utf-8'),
                    configName=self.ir['WeekendInfo']['TrackConfigName'].encode('utf-8'),
                    city=self.ir['WeekendInfo']['TrackCity'].encode('utf-8'),
                    country=self.ir['WeekendInfo']['TrackCountry'].encode('utf-8'),
                    trackGps=iracing_pb2.GPSTrack(
                        trackGpsLat=self.ir['WeekendInfo']['TrackLatitude'],
                        trackGpsLong=self.ir['WeekendInfo']['TrackLongitude'],
                        trackGpsAlt=self.ir['WeekendInfo']['TrackAltitude']
                    ),
                    length=str(self.ir['WeekendInfo']['TrackLength']),
                    turns=str(self.ir['WeekendInfo']['TrackNumTurns'])
                ),
                driver=iracing_pb2.DriverMessage(
                    driverId=str(self.ir['DriverInfo']['DriverUserID']),
                    driverName=self.ir['DriverInfo']['Drivers'][self.ir['DriverInfo']['DriverCarIdx']]['UserName'],
                    driverCar=self.ir['DriverInfo']['Drivers'][self.ir['DriverInfo']['DriverCarIdx']]['CarPath'],
                    driverCarId=str(self.ir['DriverInfo']['Drivers'][self.ir['DriverInfo']['DriverCarIdx']]['CarID']),
                    driverTeamId=str(self.ir['DriverInfo']['Drivers'][self.ir['DriverInfo']['DriverCarIdx']]['TeamID']),
                    driverSetupName=self.ir['DriverInfo']['DriverSetupName']
                )
            )
            
            response = self.stub.SendNewSession(request)
            logging.info("Response registration:" +response.message)
            return response.message == "Racing session created"
        except Exception as e:
            logging.error(f"Failed to register session: {e}")
            return False

    def send_car_setup(self) -> bool:
        """Sends the current car setup to the server"""
        if not self.state.is_connected:
            return False

        try:
            # Create car setup request
            request = iracing_pb2.SendCarSetupRequest(
                userId="898674",  # TODO: Make this configurable
                sessionId=self.state.session_id,  # Use the same session ID
                carSetup=iracing_pb2.CarSetup(
                    chassis=iracing_pb2.Chassis(
                        chassisFront=self._create_chassis_front(),
                        chassisLeftFront=self._create_chassis_front_side('LeftFront'),
                        chassisRightFront=self._create_chassis_front_side('RightFront'),
                        chassisRear=self._create_chassis_rear(),
                        chassisLeftRear=self._create_chassis_rear_side('LeftRear'),
                        chassisRightRear=self._create_chassis_rear_side('RightRear')
                    ),
                    drivetrain=self._create_drivetrain(),
                    tyresAero=self._create_tyres_aero()
                )
            )
            
            response = self.stub.SendCarSetup(request)
            return response.message == "Success"
        except Exception as e:
            logging.error(f"Failed to send car setup: {e}")
            return False

    def send_telemetry(self) -> bool:
        """Sends telemetry data to the server"""
        if not self.state.is_connected:
            return False

        try:
            request = iracing_pb2.SendTelemetryRequest(
                userId="898674",  # TODO: Make this configurable
                sessionId=self.state.session_id,  # Use the same session ID
                lap=self.ir['Lap'],
                lapCompleted=self.ir['LapCompleted'],
                lapCurrentLapTime=self.ir['LapCurrentLapTime'],
                lapDeltaToBestLap=str(self.ir['LapDeltaToBestLap']),
                lapDist=str(self.ir['LapDist']),
                lapDistPct=str(self.ir['LapDistPct']),
                lapLastLapTime=self.ir['LapLastLapTime'],
                playerCarMyIncidentCount=str(self.ir['PlayerCarMyIncidentCount']),
                playerCarTeamIncidentCount=str(self.ir['PlayerCarTeamIncidentCount']),
                brakeBias=str(self.ir['BrakeBias']),
                sector=self.ir['Sector'],
                isOnTrack=str(self.ir['IsOnTrack']),
                isInPit=str(self.ir['IsInPit']),
                isInGarage=str(self.ir['IsInGarage'])
            )
            
            response = self.stub.SendTelemetry(request)
            return response.message == "Success"
        except Exception as e:
            logging.error(f"Failed to send telemetry: {e}")
            return False

    def _create_chassis_front(self) -> iracing_pb2.ChassisFront:
        """Creates the front chassis data"""
        return iracing_pb2.ChassisFront(
            arbBlades=str(self.ir['CarSetup']['Chassis']['Front']['ArbBlades']),
            arbDriveArmLength=str(self.ir['CarSetup']['Chassis']['Front']['ArbDriveArmLength']),
            arbSize=str(self.ir['CarSetup']['Chassis']['Front']['ArbSize']),
            brakePressureBias=str(self.ir['CarSetup']['Chassis']['Front']['BrakePressureBias']),
            crossWeight=str(self.ir['CarSetup']['Chassis']['Front']['CrossWeight']),
            displayPage=str(self.ir['CarSetup']['Chassis']['Front']['DisplayPage']),
            frontMasterCylinder=str(self.ir['CarSetup']['Chassis']['Front']['FrontMasterCylinder']),
            heaveDamperDefl=str(self.ir['CarSetup']['Chassis']['Front']['HeaveDamperDefl']),
            heavePerchOffset=str(self.ir['CarSetup']['Chassis']['Front']['HeavePerchOffset']),
            heaveSpring=str(self.ir['CarSetup']['Chassis']['Front']['HeaveSpring']),
            heaveSpringDefl=str(self.ir['CarSetup']['Chassis']['Front']['HeaveSpringDefl']),
            pushrodLengthOffset=str(self.ir['CarSetup']['Chassis']['Front']['PushrodLengthOffset']),
            rearMasterCylinder=str(self.ir['CarSetup']['Chassis']['Front']['RearMasterCylinder'])
        )

    def _create_chassis_front_side(self, side: str) -> iracing_pb2.ChassisFrontSide:
        """Creates the front side chassis data"""
        return iracing_pb2.ChassisFrontSide(
            camber=str(self.ir['CarSetup']['Chassis'][side]['Camber']),
            caster=str(self.ir['CarSetup']['Chassis'][side]['Caster']),
            compDamping=str(self.ir['CarSetup']['Chassis'][side]['CompDamping']),
            cornerWeight=str(self.ir['CarSetup']['Chassis'][side]['CornerWeight']),
            rbdDamping=str(self.ir['CarSetup']['Chassis'][side]['RbdDamping']),
            rideHeight=str(self.ir['CarSetup']['Chassis'][side]['RideHeight']),
            shockDefl=str(self.ir['CarSetup']['Chassis'][side]['ShockDefl']),
            springDefl=str(self.ir['CarSetup']['Chassis'][side]['SpringDefl']),
            toeIn=str(self.ir['CarSetup']['Chassis'][side]['ToeIn']),
            torsionBarOD=str(self.ir['CarSetup']['Chassis'][side]['TorsionBarOD']),
            torsionBarPreload=str(self.ir['CarSetup']['Chassis'][side]['TorsionBarPreload'])
        )

    def _create_chassis_rear(self) -> iracing_pb2.ChassisRear:
        """Creates the rear chassis data"""
        return iracing_pb2.ChassisRear(
            arbDriveArmLength=str(self.ir['CarSetup']['Chassis']['Rear']['ArbDriveArmLength']),
            arbSize=str(self.ir['CarSetup']['Chassis']['Rear']['ArbSize']),
            brakePressureBias=str(self.ir['CarSetup']['Chassis']['Rear']['BrakePressureBias']),
            fuelLevel=str(self.ir['CarSetup']['Chassis']['Rear']['FuelLevel']),
            pushrodLengthOffset=str(self.ir['CarSetup']['Chassis']['Rear']['PushrodLengthOffset']),
            thirdDamperDefl=str(self.ir['CarSetup']['Chassis']['Rear']['ThirdDamperDefl']),
            thirdPerchOffset=str(self.ir['CarSetup']['Chassis']['Rear']['ThirdPerchOffset']),
            thirdSpring=str(self.ir['CarSetup']['Chassis']['Rear']['ThirdSpring']),
            thirdSpringDefl=str(self.ir['CarSetup']['Chassis']['Rear']['ThirdSpringDefl'])
        )

    def _create_chassis_rear_side(self, side: str) -> iracing_pb2.ChassisRearSide:
        """Creates the rear side chassis data"""
        return iracing_pb2.ChassisRearSide(
            camber=str(self.ir['CarSetup']['Chassis'][side]['Camber']),
            compDamping=str(self.ir['CarSetup']['Chassis'][side]['CompDamping']),
            cornerWeight=str(self.ir['CarSetup']['Chassis'][side]['CornerWeight']),
            cbdDamping=str(self.ir['CarSetup']['Chassis'][side]['CbdDamping']),
            rideHeight=str(self.ir['CarSetup']['Chassis'][side]['RideHeight']),
            shockDefl=str(self.ir['CarSetup']['Chassis'][side]['ShockDefl']),
            springDefl=str(self.ir['CarSetup']['Chassis'][side]['SpringDefl']),
            springPerchOffset=str(self.ir['CarSetup']['Chassis'][side]['SpringPerchOffset']),
            springRate=str(self.ir['CarSetup']['Chassis'][side]['SpringRate']),
            toeIn=str(self.ir['CarSetup']['Chassis'][side]['ToeIn'])
        )

    def _create_drivetrain(self) -> iracing_pb2.Drivetrain:
        """Creates the drivetrain data"""
        return iracing_pb2.Drivetrain(
            drivetrainDiff=iracing_pb2.DrivetrainDiff(
                diffClutchFrictionFaces=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffClutchFrictionFaces']),
                diffPreload=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffPreload']),
                diffRampAngles=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDiff']['DiffRampAngles'])
            ),
            drivetrainDt=iracing_pb2.DrivetrainDt(
                firstGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['FirstGear']),
                secondGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['SecondGear']),
                thirdGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['ThirdGear']),
                fourthGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['FourthGear']),
                fifthGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['FifthGear']),
                sixthGear=str(self.ir['CarSetup']['Drivetrain']['DrivetrainDt']['SixthGear'])
            )
        )

    def _create_tyres_aero(self) -> iracing_pb2.AeroTyres:
        """Creates the tyres and aero data"""
        return iracing_pb2.AeroTyres(
            aeroSetup=iracing_pb2.AeroSetup(
                aeroPackage=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['AeroPackage']),
                frontFlapAngle=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapAngle']),
                frontFlapConfiguration=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapConfiguration']),
                frontFlapGurneyFlap=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['FrontFlapGurneyFlap']),
                rearBeamWingAngle=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['RearBeamWingAngle']),
                rearUpperFlapAngle=str(self.ir['CarSetup']['TyresAero']['AeroSetup']['RearUpperFlapAngle'])
            ),
            aeroTyreLeftFront=self._create_aero_tyre('LeftFront'),
            aeroTyreRightFront=self._create_aero_tyre('RightFront'),
            aeroTyreLeftRear=self._create_aero_tyre('LeftRear'),
            aeroTyreRightRear=self._create_aero_tyre('RightRear')
        )

    def _create_aero_tyre(self, position: str) -> iracing_pb2.AeroTyre:
        """Creates the aero tyre data for a specific position"""
        return iracing_pb2.AeroTyre(
            coldPressure=str(self.ir['CarSetup']['TyresAero'][position]['ColdPressure']),
            lastHotPressure=str(self.ir['CarSetup']['TyresAero'][position]['LastHotPressure']),
            lastTempsOMI=str(self.ir['CarSetup']['TyresAero'][position]['LastTempsOMI']),
            treadRemaining=str(self.ir['CarSetup']['TyresAero'][position]['TreadRemaining'])
        )

    def _return_current_sector(sectors: List[Dict[str, Any]], current_percentage: float) -> int:
        """Returns the current sector based on the percentage of the lap"""
        for sector in sectors:
            if current_percentage <= sector['SectorStartPct']:
                return sector['Number']
        return len(sectors)


    def update_session_state(self):
        """Updates the session state based on current iRacing data"""
        if not self.state.is_connected:
            return

        # Update on-track state
        self.state.is_on_track = self.ir['IsOnTrack']
        if not self.state.is_on_track:
            logging.info("Not on track")
            return
        
        # Update lap and sector information
        current_lap = self.ir['Lap']
        current_sector = self._return_current_sector(self.ir['SplitTimeInfo']['Sectors'], self.ir['LapDistPct'])

        # Check if outlap is completed (first lap after pit)
        if current_lap > self.state.current_lap and self.state.current_lap == 0:
            self.state.outlap_completed = True

        # Update sector completion
        if current_sector > self.state.last_sector:
            self.state.last_sector = current_sector

        self.state.current_lap = current_lap

    def check_iracing(self):
        """Checks if iRacing is running"""
        if not self.state.is_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            self.state.is_connected = True
            logging.info('irsdk connected')

    def run(self):
        """Main loop for the iRacing client"""
        logging.info("Starting IRacingSetups client - environment %s", environment)

        while True:
            try:
                # Check if iRacing is running
                if self.state.is_connected:
                    # Connect to gRPC if not already connected
                    logging.info("iRacing is running")
                    if not self.channel:
                        self.connect_to_grpc()
                    logging.info("Connected to gRPC")
                    
                    # Register session if not already registered
                    if not self.state.is_registered:
                        logging.info("Registering session")
                        if self.register_session():
                            self.state.is_registered = True
                            logging.info(f"Session registered successfully with ID: {self.state.session_id}")

                    # Update session state
                    self.update_session_state()
                    logging.info("Session state updated")

                    # Send car setup if session is registered and setup hasn't been sent
                    if self.state.is_registered and not self.state.car_setup_sent:
                        logging.info("Sending car setup")
                        if self.send_car_setup():
                            self.state.car_setup_sent = True
                            logging.info("Car setup sent successfully")

                    # Send telemetry if all conditions are met
                    if (self.state.is_registered and 
                        self.state.is_on_track and 
                        self.state.outlap_completed and 
                        self.state.last_sector > 0):
                        logging.info("Sending telemetry")
                        self.send_telemetry()

                else:
                    # Disconnect from gRPC if iRacing is not running
                    logging.info("iRacing is not running") 
                    self.disconnect_from_grpc()
                    # Reset session state
                    self.state = SessionState()

                    self.check_iracing()

                # Sleep to prevent excessive CPU usage
                time.sleep(0.1)

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(1)  # Sleep longer on error


def main():
    # Initialize logging configuration
    logging.config.dictConfig(config)
    
    # Set the root logger level to INFO to ensure INFO messages are visible
    logging.getLogger().setLevel(logging.INFO)
    
    # Create and run the client
    client = IRacingClient()
    client.run()


if __name__ == "__main__":
    main()