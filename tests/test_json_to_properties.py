import unittest
import json
from iracingsetups_client.json_to_properties import flatten_json

class TestFlattenJson(unittest.TestCase):
    def test_flatten_json(self):
        # Test data provided in the issue description
        test_data = {
            0: [
                {
                    "currentLapTime": 0,
                    "lapNumber": 0,
                    "sectorNumber": 5
                }
            ],
            1: [
                {
                    "currentLapTime": 26.983465,
                    "lapNumber": 1,
                    "sectorNumber": 1
                },
                {
                    "currentLapTime": 43.5168,
                    "lapNumber": 1,
                    "sectorNumber": 2
                },
                {
                    "currentLapTime": 67.8668,
                    "lapNumber": 1,
                    "sectorNumber": 3
                },
                {
                    "currentLapTime": 86.3668,
                    "lapNumber": 1,
                    "sectorNumber": 4
                },
                {
                    "currentLapTime": 0,
                    "lapNumber": 1,
                    "sectorNumber": 5
                }
            ],
            2: [
                {
                    "currentLapTime": 367.9903,
                    "lapNumber": 2,
                    "sectorNumber": 1
                },
                {
                    "currentLapTime": 393.82364,
                    "lapNumber": 2,
                    "sectorNumber": 2
                },
                {
                    "currentLapTime": 430.37363,
                    "lapNumber": 2,
                    "sectorNumber": 3
                },
                {
                    "currentLapTime": 467.47363,
                    "lapNumber": 2,
                    "sectorNumber": 4
                },
                {
                    "currentLapTime": 101.9265,
                    "lapNumber": 2,
                    "sectorNumber": 5
                }
            ],
            3: [
                {
                    "currentLapTime": 85.3912,
                    "lapNumber": 3,
                    "sectorNumber": 1
                },
                {
                    "currentLapTime": 102.65787,
                    "lapNumber": 3,
                    "sectorNumber": 2
                },
                {
                    "currentLapTime": 126.757866,
                    "lapNumber": 3,
                    "sectorNumber": 3
                },
                {
                    "currentLapTime": 145.6912,
                    "lapNumber": 3,
                    "sectorNumber": 4
                },
                {
                    "currentLapTime": -1,
                    "lapNumber": 3,
                    "sectorNumber": 5
                }
            ],
            4: [
                {
                    "currentLapTime": 27.248133,
                    "lapNumber": 4,
                    "sectorNumber": 1
                },
                {
                    "currentLapTime": 43.49813,
                    "lapNumber": 4,
                    "sectorNumber": 2
                },
                {
                    "currentLapTime": 67.14813,
                    "lapNumber": 4,
                    "sectorNumber": 3
                },
                {
                    "currentLapTime": 85.681465,
                    "lapNumber": 4,
                    "sectorNumber": 4
                },
                {
                    "currentLapTime": 161.4764,
                    "lapNumber": 4,
                    "sectorNumber": 5
                }
            ],
            5: [
                {
                    "currentLapTime": 27.707066,
                    "lapNumber": 5,
                    "sectorNumber": 1
                },
                {
                    "currentLapTime": 46.4904,
                    "lapNumber": 5,
                    "sectorNumber": 2
                },
                {
                    "currentLapTime": 71.390396,
                    "lapNumber": 5,
                    "sectorNumber": 3
                },
                {
                    "currentLapTime": 91.7404,
                    "lapNumber": 5,
                    "sectorNumber": 4
                },
                {
                    "currentLapTime": 101.9744,
                    "lapNumber": 5,
                    "sectorNumber": 5
                }
            ]
        }
        
        # Flatten the JSON
        flattened = flatten_json(test_data)
        
        # Verify some expected key-value pairs
        # Lap 0
        self.assertEqual(flattened["0.0.currentLapTime"], 0)
        self.assertEqual(flattened["0.0.lapNumber"], 0)
        self.assertEqual(flattened["0.0.sectorNumber"], 5)
        
        # Lap 1
        self.assertEqual(flattened["1.0.currentLapTime"], 26.983465)
        self.assertEqual(flattened["1.0.lapNumber"], 1)
        self.assertEqual(flattened["1.0.sectorNumber"], 1)
        
        self.assertEqual(flattened["1.4.currentLapTime"], 0)
        self.assertEqual(flattened["1.4.lapNumber"], 1)
        self.assertEqual(flattened["1.4.sectorNumber"], 5)
        
        # Lap 3 (includes negative value)
        self.assertEqual(flattened["3.4.currentLapTime"], -1)
        self.assertEqual(flattened["3.4.lapNumber"], 3)
        self.assertEqual(flattened["3.4.sectorNumber"], 5)
        
        # Lap 5
        self.assertEqual(flattened["5.4.currentLapTime"], 101.9744)
        self.assertEqual(flattened["5.4.lapNumber"], 5)
        self.assertEqual(flattened["5.4.sectorNumber"], 5)
        
        # Check total number of keys
        # Each lap has 5 sectors (except lap 0 which has 1), each sector has 3 properties
        # So total keys should be: (1 + 5 + 5 + 5 + 5 + 5) * 3 = 78
        self.assertEqual(len(flattened), 78)

        with open('./session_tracking.properties', 'w+') as f:
            for key, value in flattened.items():
                f.write(f"{key}={value}\n")
            f.write("")
            f.close()

    def test_flatten_json_with_prefix(self):
        # Test with a prefix
        test_data = {"a": 1, "b": {"c": 2}}
        flattened = flatten_json(test_data, prefix="test")
        
        self.assertEqual(flattened["test.a"], 1)
        self.assertEqual(flattened["test.b.c"], 2)

    def test_flatten_json_empty(self):
        # Test with empty input
        self.assertEqual(flatten_json({}), {})
        self.assertEqual(flatten_json([]), {})
