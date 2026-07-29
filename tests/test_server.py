"""
Tests for Redfish REST API Server endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from src.server.app import app


class TestRedfishServerAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_service_root_endpoint(self):
        response = self.client.get("/redfish/v1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("OData-Version"), "4.0")

        data = response.json()
        self.assertEqual(data["@odata.id"], "/redfish/v1/")
        self.assertEqual(data["RedfishVersion"], "1.17.0")

    def test_chassis_collection_and_member(self):
        resp_coll = self.client.get("/redfish/v1/Chassis")
        self.assertEqual(resp_coll.status_code, 200)
        self.assertEqual(resp_coll.json()["Members@odata.count"], 1)

        resp_chassis = self.client.get("/redfish/v1/Chassis/1")
        self.assertEqual(resp_chassis.status_code, 200)
        self.assertEqual(resp_chassis.json()["Id"], "1")

    def test_cooling_loop_endpoint(self):
        response = self.client.get("/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["@odata.id"], "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1")
        self.assertIn("SupplyTemperatureCelsius", data)
        self.assertIn("ReturnTemperatureCelsius", data)
        self.assertGreater(data["ReturnTemperatureCelsius"], data["SupplyTemperatureCelsius"])

    def test_sensors_collection_and_readings(self):
        resp_coll = self.client.get("/redfish/v1/Chassis/1/Sensors")
        self.assertEqual(resp_coll.status_code, 200)
        self.assertEqual(resp_coll.json()["Members@odata.count"], 5)

        resp_sensor = self.client.get("/redfish/v1/Chassis/1/Sensors/SupplyTemp")
        self.assertEqual(resp_sensor.status_code, 200)
        data = resp_sensor.json()
        self.assertEqual(data["Id"], "SupplyTemp")
        self.assertEqual(data["ReadingUnits"], "Cel")

    def test_nonexistent_sensor_returns_404(self):
        response = self.client.get("/redfish/v1/Chassis/1/Sensors/InvalidSensorID")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
