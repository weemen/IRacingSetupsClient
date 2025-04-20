from grpc import Channel
from irsdk import IRSDK

from iracingsetups_client import iracing_pb2
from iracingsetups_client.iracing_pb2_grpc import IracingServiceStub


def register_new_session_message(ir: IRSDK, stub: IracingServiceStub):
    return stub.SendNewSession(
        iracing_pb2.SendNewSessionRequest(
            userId="898674",
            sessionId=str(ir['WeekendInfo']['SessionID']),
            track=iracing_pb2.TrackMessage(
                trackId=str(ir['WeekendInfo']['TrackID']),
                name=f"{ir['WeekendInfo']['TrackDisplayName']} ({ir['WeekendInfo']['TrackName']})",
                configName=ir['WeekendInfo']['TrackConfigName'],
                city=ir['WeekendInfo']['TrackCity'],
                country=ir['WeekendInfo']['TrackCountry'],
                trackGps=iracing_pb2.GPSTrack(
                    trackGpsLat=ir['WeekendInfo']['TrackLatitude'],
                    trackGpsLong=ir['WeekendInfo']['TrackLongitude'],
                    trackGpsAlt=ir['WeekendInfo']['TrackAltitude']
                ),
                length=ir['WeekendInfo']['TrackLength'],
                turns=str(ir['WeekendInfo']['TrackNumTurns'])
            ),
            driver=iracing_pb2.DriverMessage(
                driverId=str(ir['DriverInfo']['Drivers'][0]['UserID']),
                driverName=ir['DriverInfo']['Drivers'][0]['UserName'],
                driverCar=ir['DriverInfo']['Drivers'][0]['CarScreenName'],
                driverCarId=str(ir['DriverInfo']['Drivers'][0]['CarID']),
                driverTeamId=str(ir['DriverInfo']['Drivers'][0]['TeamID']),
                driverSetupName=ir['DriverInfo']['Drivers'][0]['DriverSetupName'],
            )
        ))
