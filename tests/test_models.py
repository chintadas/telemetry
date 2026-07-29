"""
Tests for Redfish Pydantic data models.
"""

import unittest
from src.redfish.models import ServiceRoot, CoolingLoopResource, SensorReading


class TestRedfishModels(unittest.TestCase):

    def test_service_root_defaults(self):
        root = ServiceRoot()
        data = root.model_dump(by_alias=True)

        self.assertEqual(data["@odata.id"], "/redfish/v1/")
        self.assertEqual(data["@odata.type"], "#ServiceRoot.v1_13_0.ServiceRoot")
        self.assertEqual(data["Id"], "RootService")
        self.assertEqual(data["RedfishVersion"], "1.17.0")

    def test_cooling_loop_resource(self):
        loop = CoolingLoopResource(
            **{
                "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1",
                "@odata.type": "#CoolingLoop.v1_0_0.CoolingLoop",
                "Id": "Loop1",
                "Name": "Primary Liquid Cooling Loop",
                "SupplyTemperatureCelsius": 25.5,
                "ReturnTemperatureCelsius": 35.2,
                "FlowRateLPM": 45.0,
                "PressurekPa": 220.0,
            }
        )

        data = loop.model_dump(by_alias=True)
        self.assertEqual(data["@odata.id"], "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1")
        self.assertEqual(data["SupplyTemperatureCelsius"], 25.5)
        self.assertEqual(data["ReturnTemperatureCelsius"], 35.2)
        self.assertEqual(data["FlowRateLPM"], 45.0)
        self.assertEqual(data["Status"]["Health"], "OK")

    def test_sensor_reading(self):
        sensor = SensorReading(
            **{
                "@odata.id": "/redfish/v1/Chassis/1/Sensors/SupplyTemp1",
                "@odata.type": "#Sensor.v1_2_0.Sensor",
                "Id": "SupplyTemp1",
                "Name": "Supply Temp Sensor 1",
                "Reading": 24.8,
                "ReadingUnits": "Cel",
            }
        )

        data = sensor.model_dump(by_alias=True)
        self.assertEqual(data["Reading"], 24.8)
        self.assertEqual(data["ReadingUnits"], "Cel")


if __name__ == "__main__":
    unittest.main()
