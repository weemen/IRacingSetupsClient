import logging
import logging.config
import time
import uuid
from dataclasses import dataclass

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
import irsdk

import iracingsetups_client.iracing_pb2 as iracing_pb2
from iracingsetups_client.config import environment, config
from iracingsetups_client.iracing_pb2_grpc import IracingServiceStub
from iracingsetups_client.tracking_client import TrackingClient


@dataclass
class SessionState:
    """Tracks the state of the current iRacing session"""
    is_connected = False
    is_registered: bool = False
    car_setup_sent: bool = False
    is_on_track: bool = False
    is_in_pit: bool = False
    outlap_completed: bool = False
    last_sector: int = 0
    previous_sector: int = 0
    sector_changed: bool = False
    current_lap: int = 0
    session_id: str = ""  # Store the UUID for the current session


class IRacingClient:
    def __init__(self, tracking_file_path: str = "session_tracking.json"):
        self.host = config["backend_domain"]+":"+str(config["grpc_port"])
        self.tracking_file_path = tracking_file_path
        self.ir = irsdk.IRSDK()
        self.state = SessionState()
        self.channel = None
        self.stub = None
        self.tracking_client = TrackingClient(
            user_id=config["iracing_user_id"],
            domain=config["backend_domain"],
            port=config["http_port"],
            base_dir=config["storage_path"]
        )

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
                userId=config["iracing_user_id"],
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
                ),
                dateTime=Timestamp()
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
                userId=config["iracing_user_id"],
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
                ),
                dateTime=Timestamp()
            )
            
            response = self.stub.SendCarSetup(request)
            return response.message == "Car setup registered"
        except Exception as e:
            logging.error(f"Failed to send car setup: {e}")
            return False

    def send_telemetry(self) -> bool:
        """Sends telemetry data to the server"""
        if not self.state.is_connected:
            return False

        try:
            lap = self.ir['Lap']
            logging.info("Lap: %s | Sector: %s", lap, self.state.last_sector)
            if self.state.last_sector == 1 and lap > 0:
                lap = self.ir['Lap'] - 1

            last_sector_time = self.ir['LapCurrentLapTime']
            if self.state.previous_sector == len(self.ir['SplitTimeInfo']['Sectors']) and lap > 0:
                last_sector_time = self.ir['LapLastLapTime']

            request = iracing_pb2.SendTelemetryRequest(
                userId=config["iracing_user_id"],  # Use configured user ID
                sessionId=self.state.session_id,  # Use the same session ID
                lap=lap,
                lapCompleted=self.ir['LapCompleted'],
                lapCurrentLapTime=last_sector_time,
                lapDeltaToBestLap=str(self.ir['LapDeltaToBestLap']),
                lapDist=str(self.ir['LapDist']),
                lapDistPct=str(self.ir['LapDistPct']),
                lapLastLapTime=self.ir['LapLastLapTime'],
                playerCarMyIncidentCount=str(self.ir['PlayerCarMyIncidentCount']),
                playerCarTeamIncidentCount=str(self.ir['PlayerCarTeamIncidentCount']),
                brakeBias=str(self.ir['BrakeBias']),
                sector=self.state.previous_sector,
                isOnTrack=str(self.ir['IsOnTrack']),
                isInPit=str(self.state.is_in_pit),
                isInGarage=str(self.ir['IsInGarage']),
                dateTime=Timestamp()
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
            brakePressureBias=self.ir['CarSetup']['Chassis']['Front']['BrakePressureBias'],
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
        bb_front = self.ir['CarSetup']['Chassis']['Front']['BrakePressureBias'].replace('%', '')
        bb_rear = str(100.0 - float(bb_front))+ "%"
        return iracing_pb2.ChassisRear(
            arbDriveArmLength=str(self.ir['CarSetup']['Chassis']['Rear']['ArbDriveArmLength']),
            arbSize=str(self.ir['CarSetup']['Chassis']['Rear']['ArbSize']),
            brakePressureBias=bb_rear,
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
            rbdDamping=str(self.ir['CarSetup']['Chassis'][side]['RbdDamping']),
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
                diffClutchFrictionFaces=str(self.ir['CarSetup']['Drivetrain']['Diff']['DiffClutchFrictionFaces']),
                diffPreload=str(self.ir['CarSetup']['Drivetrain']['Diff']['DiffPreload']),
                diffRampAngles=str(self.ir['CarSetup']['Drivetrain']['Diff']['DiffRampAngles'])
            ),
            drivetrainDt=iracing_pb2.DrivetrainDt(
                firstGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['FirstGear']),
                secondGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['SecondGear']),
                thirdGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['ThirdGear']),
                fourthGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['FourthGear']),
                fifthGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['FifthGear']),
                sixthGear=str(self.ir['CarSetup']['Drivetrain']['Drivetrain']['SixthGear'])
            )
        )

    def _create_tyres_aero(self) -> iracing_pb2.AeroTyres:
        """Creates the tyres and aero data"""
        return iracing_pb2.AeroTyres(
            aeroSetup=iracing_pb2.AeroSetup(
                aeroPackage=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['AeroPackage']),
                frontFlapAngle=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['FrontFlapAngle']),
                frontFlapConfiguration=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['FrontFlapConfiguration']),
                frontFlapGurneyFlap=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['FrontFlapGurneyFlap']),
                rearBeamWingAngle=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['RearBeamWingAngle']),
                rearUpperFlapAngle=str(self.ir['CarSetup']['TiresAero']['AeroSetup']['RearUpperFlapAngle'])
            ),
            aeroTyreLeftFront=self._create_aero_tyre('LeftFront'),
            aeroTyreRightFront=self._create_aero_tyre('RightFront'),
            aeroTyreLeftRear=self._create_aero_tyre('LeftRear'),
            aeroTyreRightRear=self._create_aero_tyre('RightRear')
        )

    def _create_aero_tyre(self, position: str) -> iracing_pb2.AeroTyre:
        """Creates the aero tyre data for a specific position"""
        if "Left" in position:
            temps = self.ir['CarSetup']['TiresAero'][position]['LastTempsOMI']
        else:
            t = self.ir['CarSetup']['TiresAero'][position]['LastTempsIMO'].split(", ")
            t.reverse()
            temps = ", ".join(t)
        return iracing_pb2.AeroTyre(
            coldPressure=str(self.ir['CarSetup']['TiresAero'][position]['ColdPressure']),
            lastHotPressure=str(self.ir['CarSetup']['TiresAero'][position]['LastHotPressure']),
            lastTempsOMI=temps,
            treadRemaining=str(self.ir['CarSetup']['TiresAero'][position]['TreadRemaining'])
        )

    def _return_current_sector(self, sectors, current_percentage) -> int:
        """Returns the current sector based on the percentage of the lap"""
        for sector in sectors:
            if current_percentage <= sector['SectorStartPct']:
                return sector['SectorNum']
        return len(sectors)

    def update_session_state(self):
        """Updates the session state based on current iRacing data"""
        if not self.state.is_connected:
            return

        # Update on-track state
        self.state.is_on_track = self.ir['IsOnTrack'] and not self.ir['OnPitRoad']
        self.state.is_in_pit = self.ir['IsOnTrack'] and self.ir['OnPitRoad']
    
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
        if current_sector != self.state.last_sector:
            self.state.previous_sector = self.state.last_sector
            self.state.last_sector = current_sector
            self.state.sector_changed = True
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
                    logging.debug("iRacing is running")
                    if not self.channel:
                        self.connect_to_grpc()
                    # logging.debug("Connected to gRPC")
                    
                    # Register session if not already registered
                    if not self.state.is_registered:
                        logging.info("Registering session")
                        if self.register_session():
                            self.state.is_registered = True
                            logging.info(f"Session registered successfully with ID: {self.state.session_id}")

                    # Update session state
                    self.update_session_state()
                    logging.debug("Session state updated")

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
                        self.state.sector_changed and
                        self.state.last_sector > 0):
                        # logging.info("Sending telemetry: LAP %s, SECTOR %s", self.state.current_lap, self.state.last_sector)
                        self.state.sector_changed = False
                        self.send_telemetry()
                        time.sleep(2)
                        self.tracking_client.update_session_tracking(self.state.session_id)

                else:
                    # Disconnect from gRPC if iRacing is not running
                    logging.info("iRacing is not running") 
                    self.disconnect_from_grpc()
                    # Reset session state
                    self.state = SessionState()

                    self.check_iracing()

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(1)  # Sleep longer on error


def main():
    # Initialize logging configuration
    logging.config.dictConfig(config)
    
    # Set the root logger level to INFO to ensure INFO messages are visible
    logging.getLogger().setLevel(logging.INFO)
    if not config["iracing_user_id"]:
        logging.error("IRacing user id is not set")
        return

    # Create and run the client
    client = IRacingClient()
    client.run()


if __name__ == "__main__":
    main()