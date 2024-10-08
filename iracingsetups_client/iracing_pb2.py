# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: iracingsetups_client/iracing.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\"iracingsetups_client/iracing.proto\"x\n\x15SendNewSessionRequest\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x11\n\tsessionId\x18\x02 \x01(\t\x12\x1c\n\x05track\x18\x03 \x01(\x0b\x32\r.TrackMessage\x12\x1e\n\x06\x64river\x18\x04 \x01(\x0b\x32\x0e.DriverMessage\"U\n\x13SendCarSetupRequest\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x11\n\tsessionId\x18\x02 \x01(\t\x12\x1b\n\x08\x63\x61rSetup\x18\x03 \x01(\x0b\x32\t.CarSetup\"\x9c\x01\n\x0cTrackMessage\x12\x0f\n\x07trackId\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nconfigName\x18\x03 \x01(\t\x12\x0c\n\x04\x63ity\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\x12\x1b\n\x08trackGps\x18\x06 \x01(\x0b\x32\t.GPSTrack\x12\x0e\n\x06length\x18\x07 \x01(\t\x12\r\n\x05turns\x18\x08 \x01(\t\"J\n\x08GPSTrack\x12\x13\n\x0btrackGpsLat\x18\x01 \x01(\t\x12\x14\n\x0ctrackGpsLong\x18\x02 \x01(\t\x12\x13\n\x0btrackGpsAlt\x18\x03 \x01(\t\"\x8c\x01\n\rDriverMessage\x12\x10\n\x08\x64riverId\x18\x01 \x01(\t\x12\x12\n\ndriverName\x18\x02 \x01(\t\x12\x11\n\tdriverCar\x18\x03 \x01(\t\x12\x13\n\x0b\x64riverCarId\x18\x04 \x01(\t\x12\x14\n\x0c\x64riverTeamId\x18\x05 \x01(\t\x12\x17\n\x0f\x64riverSetupName\x18\x06 \x01(\t\"e\n\x08\x43\x61rSetup\x12\x19\n\x07\x63hassis\x18\x01 \x01(\x0b\x32\x08.Chassis\x12\x1f\n\ndrivetrain\x18\x02 \x01(\x0b\x32\x0b.Drivetrain\x12\x1d\n\ttyresAero\x18\x03 \x01(\x0b\x32\n.AeroTyres\"\x83\x02\n\x07\x43hassis\x12#\n\x0c\x63hassisFront\x18\x01 \x01(\x0b\x32\r.ChassisFront\x12+\n\x10\x63hassisLeftFront\x18\x02 \x01(\x0b\x32\x11.ChassisFrontSide\x12,\n\x11\x63hassisRightFront\x18\x03 \x01(\x0b\x32\x11.ChassisFrontSide\x12!\n\x0b\x63hassisRear\x18\x04 \x01(\x0b\x32\x0c.ChassisRear\x12)\n\x0f\x63hassisLeftRear\x18\x05 \x01(\x0b\x32\x10.ChassisRearSide\x12*\n\x10\x63hassisRightRear\x18\x06 \x01(\x0b\x32\x10.ChassisRearSide\"\xc9\x02\n\x0c\x43hassisFront\x12\x11\n\tarbBlades\x18\x01 \x01(\t\x12\x19\n\x11\x61rbDriveArmLength\x18\x02 \x01(\t\x12\x0f\n\x07\x61rbSize\x18\x03 \x01(\t\x12\x19\n\x11\x62rakePressureBias\x18\x04 \x01(\t\x12\x13\n\x0b\x63rossWeight\x18\x05 \x01(\t\x12\x13\n\x0b\x64isplayPage\x18\x06 \x01(\t\x12\x1b\n\x13\x66rontMasterCylinder\x18\x07 \x01(\t\x12\x17\n\x0fheaveDamperDefl\x18\x08 \x01(\t\x12\x18\n\x10heavePerchOffset\x18\t \x01(\t\x12\x13\n\x0bheaveSpring\x18\n \x01(\t\x12\x17\n\x0fheaveSpringDefl\x18\x0b \x01(\t\x12\x1b\n\x13pushrodLengthOffset\x18\x0c \x01(\t\x12\x1a\n\x12rearMasterCylinder\x18\r \x01(\t\"\xec\x01\n\x10\x43hassisFrontSide\x12\x0e\n\x06\x63\x61mber\x18\x01 \x01(\t\x12\x0e\n\x06\x63\x61ster\x18\x02 \x01(\t\x12\x13\n\x0b\x63ompDamping\x18\x03 \x01(\t\x12\x14\n\x0c\x63ornerWeight\x18\x04 \x01(\t\x12\x12\n\nrbdDamping\x18\x05 \x01(\t\x12\x12\n\nrideHeight\x18\x06 \x01(\t\x12\x11\n\tshockDefl\x18\x07 \x01(\t\x12\x12\n\nspringDefl\x18\x08 \x01(\t\x12\r\n\x05toeIn\x18\t \x01(\t\x12\x14\n\x0ctorsionBarOD\x18\n \x01(\t\x12\x19\n\x11torsionBarPreload\x18\x0b \x01(\t\"\xe5\x01\n\x0b\x43hassisRear\x12\x19\n\x11\x61rbDriveArmLength\x18\x01 \x01(\t\x12\x0f\n\x07\x61rbSize\x18\x02 \x01(\t\x12\x19\n\x11\x62rakePressureBias\x18\x03 \x01(\t\x12\x11\n\tfuelLevel\x18\x04 \x01(\t\x12\x1b\n\x13pushrodLengthOffset\x18\x05 \x01(\t\x12\x17\n\x0fthirdDamperDefl\x18\x06 \x01(\t\x12\x18\n\x10thirdPerchOffset\x18\x07 \x01(\t\x12\x13\n\x0bthirdSpring\x18\x08 \x01(\t\x12\x17\n\x0fthirdSpringDefl\x18\t \x01(\t\"\xd9\x01\n\x0f\x43hassisRearSide\x12\x0e\n\x06\x63\x61mber\x18\x01 \x01(\t\x12\x13\n\x0b\x63ompDamping\x18\x02 \x01(\t\x12\x14\n\x0c\x63ornerWeight\x18\x03 \x01(\t\x12\x12\n\ncbdDamping\x18\x04 \x01(\t\x12\x12\n\nrideHeight\x18\x05 \x01(\t\x12\x11\n\tshockDefl\x18\x06 \x01(\t\x12\x12\n\nspringDefl\x18\x07 \x01(\t\x12\x19\n\x11springPerchOffset\x18\x08 \x01(\t\x12\x12\n\nspringRate\x18\t \x01(\t\x12\r\n\x05toeIn\x18\n \x01(\t\"Z\n\nDrivetrain\x12\'\n\x0e\x64rivetrainDiff\x18\x01 \x01(\x0b\x32\x0f.DrivetrainDiff\x12#\n\x0c\x64rivetrainDt\x18\x02 \x01(\x0b\x32\r.DrivetrainDt\"^\n\x0e\x44rivetrainDiff\x12\x1f\n\x17\x64iffClutchFrictionFaces\x18\x01 \x01(\t\x12\x13\n\x0b\x64iffPreload\x18\x02 \x01(\t\x12\x16\n\x0e\x64iffRampAngles\x18\x03 \x01(\t\"\x82\x01\n\x0c\x44rivetrainDt\x12\x11\n\tfirstGear\x18\x01 \x01(\t\x12\x12\n\nsecondGear\x18\x02 \x01(\t\x12\x11\n\tthirdGear\x18\x03 \x01(\t\x12\x12\n\nfourthGear\x18\x04 \x01(\t\x12\x11\n\tfifthGear\x18\x05 \x01(\t\x12\x11\n\tsixthGear\x18\x06 \x01(\t\"\xc2\x01\n\tAeroTyres\x12\x1d\n\taeroSetup\x18\x01 \x01(\x0b\x32\n.AeroSetup\x12$\n\x11\x61\x65roTyreLeftFront\x18\x02 \x01(\x0b\x32\t.AeroTyre\x12%\n\x12\x61\x65roTyreRightFront\x18\x03 \x01(\x0b\x32\t.AeroTyre\x12#\n\x10\x61\x65roTyreLeftRear\x18\x04 \x01(\x0b\x32\t.AeroTyre\x12$\n\x11\x61\x65roTyreRightRear\x18\x05 \x01(\x0b\x32\t.AeroTyre\"\xac\x01\n\tAeroSetup\x12\x13\n\x0b\x61\x65roPackage\x18\x01 \x01(\t\x12\x16\n\x0e\x66rontFlapAngle\x18\x02 \x01(\t\x12\x1e\n\x16\x66rontFlapConfiguration\x18\x03 \x01(\t\x12\x1b\n\x13\x66rontFlapGurneyFlap\x18\x04 \x01(\t\x12\x19\n\x11rearBeamWingAngle\x18\x05 \x01(\t\x12\x1a\n\x12rearUpperFlapAngle\x18\x06 \x01(\t\"g\n\x08\x41\x65roTyre\x12\x14\n\x0c\x63oldPressure\x18\x01 \x01(\t\x12\x17\n\x0flastHotPressure\x18\x02 \x01(\t\x12\x14\n\x0clastTempsOMI\x18\x03 \x01(\t\x12\x16\n\x0etreadRemaining\x18\x04 \x01(\t\")\n\rSplitTimeInfo\x12\x18\n\x07sectors\x18\x01 \x03(\x0b\x32\x07.Sector\"3\n\x06Sector\x12\x11\n\tsectorNum\x18\x01 \x01(\t\x12\x16\n\x0eSectorStartPct\x18\x02 \x01(\t\"\xf0\x02\n\x14SendTelemetryRequest\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x11\n\tsessionId\x18\x02 \x01(\t\x12\x0b\n\x03lap\x18\x03 \x01(\x05\x12\x14\n\x0clapCompleted\x18\x04 \x01(\x05\x12\x19\n\x11lapCurrentLapTime\x18\x05 \x01(\x02\x12\x19\n\x11lapDeltaToBestLap\x18\x06 \x01(\t\x12\x0f\n\x07lapDist\x18\x07 \x01(\t\x12\x12\n\nlapDistPct\x18\x08 \x01(\t\x12\x16\n\x0elapLastLapTime\x18\t \x01(\x02\x12 \n\x18playerCarMyIncidentCount\x18\n \x01(\t\x12\"\n\x1aplayerCarTeamIncidentCount\x18\x0b \x01(\t\x12\x11\n\tbrakeBias\x18\x0c \x01(\t\x12\x0e\n\x06sector\x18\r \x01(\x05\x12\x11\n\tisOnTrack\x18\x0e \x01(\t\x12\x0f\n\x07isInPit\x18\x0f \x01(\t\x12\x12\n\nisInGarage\x18\x10 \x01(\t\"8\n\x13SendTyreDataRequest\x12\x0e\n\x06userId\x18\x01 \x01(\t\x12\x11\n\tsessionId\x18\x02 \x01(\t\"\x1e\n\x0bSucessReply\x12\x0f\n\x07message\x18\x01 \x01(\t2\xee\x01\n\x0eIracingService\x12\x38\n\x0eSendNewSession\x12\x16.SendNewSessionRequest\x1a\x0c.SucessReply\"\x00\x12\x34\n\x0cSendCarSetup\x12\x14.SendCarSetupRequest\x1a\x0c.SucessReply\"\x00\x12\x36\n\rSendTelemetry\x12\x15.SendTelemetryRequest\x1a\x0c.SucessReply\"\x00\x12\x34\n\x0cSendTyreData\x12\x14.SendTyreDataRequest\x1a\x0c.SucessReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'iracingsetups_client.iracing_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SENDNEWSESSIONREQUEST']._serialized_start=38
  _globals['_SENDNEWSESSIONREQUEST']._serialized_end=158
  _globals['_SENDCARSETUPREQUEST']._serialized_start=160
  _globals['_SENDCARSETUPREQUEST']._serialized_end=245
  _globals['_TRACKMESSAGE']._serialized_start=248
  _globals['_TRACKMESSAGE']._serialized_end=404
  _globals['_GPSTRACK']._serialized_start=406
  _globals['_GPSTRACK']._serialized_end=480
  _globals['_DRIVERMESSAGE']._serialized_start=483
  _globals['_DRIVERMESSAGE']._serialized_end=623
  _globals['_CARSETUP']._serialized_start=625
  _globals['_CARSETUP']._serialized_end=726
  _globals['_CHASSIS']._serialized_start=729
  _globals['_CHASSIS']._serialized_end=988
  _globals['_CHASSISFRONT']._serialized_start=991
  _globals['_CHASSISFRONT']._serialized_end=1320
  _globals['_CHASSISFRONTSIDE']._serialized_start=1323
  _globals['_CHASSISFRONTSIDE']._serialized_end=1559
  _globals['_CHASSISREAR']._serialized_start=1562
  _globals['_CHASSISREAR']._serialized_end=1791
  _globals['_CHASSISREARSIDE']._serialized_start=1794
  _globals['_CHASSISREARSIDE']._serialized_end=2011
  _globals['_DRIVETRAIN']._serialized_start=2013
  _globals['_DRIVETRAIN']._serialized_end=2103
  _globals['_DRIVETRAINDIFF']._serialized_start=2105
  _globals['_DRIVETRAINDIFF']._serialized_end=2199
  _globals['_DRIVETRAINDT']._serialized_start=2202
  _globals['_DRIVETRAINDT']._serialized_end=2332
  _globals['_AEROTYRES']._serialized_start=2335
  _globals['_AEROTYRES']._serialized_end=2529
  _globals['_AEROSETUP']._serialized_start=2532
  _globals['_AEROSETUP']._serialized_end=2704
  _globals['_AEROTYRE']._serialized_start=2706
  _globals['_AEROTYRE']._serialized_end=2809
  _globals['_SPLITTIMEINFO']._serialized_start=2811
  _globals['_SPLITTIMEINFO']._serialized_end=2852
  _globals['_SECTOR']._serialized_start=2854
  _globals['_SECTOR']._serialized_end=2905
  _globals['_SENDTELEMETRYREQUEST']._serialized_start=2908
  _globals['_SENDTELEMETRYREQUEST']._serialized_end=3276
  _globals['_SENDTYREDATAREQUEST']._serialized_start=3278
  _globals['_SENDTYREDATAREQUEST']._serialized_end=3334
  _globals['_SUCESSREPLY']._serialized_start=3336
  _globals['_SUCESSREPLY']._serialized_end=3366
  _globals['_IRACINGSERVICE']._serialized_start=3369
  _globals['_IRACINGSERVICE']._serialized_end=3607
# @@protoc_insertion_point(module_scope)
