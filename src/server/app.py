"""
FastAPI Redfish REST API implementation for Liquid Cooling Loop Telemetry Engine.
"""

from fastapi import FastAPI, Response, HTTPException
from src.redfish.models import ServiceRoot, CoolingLoopResource, SensorReading
from src.engine.simulator import CoolingLoopSimulator

app = FastAPI(
    title="Redfish Liquid Cooling Telemetry Engine Mock",
    version="1.0.0",
    description="Simulates data center liquid cooling telemetry conforming to DMTF Redfish standards.",
)

# Global simulator instance
simulator = CoolingLoopSimulator(loop_id="1")


@app.middleware("http")
async def add_redfish_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["OData-Version"] = "4.0"
    return response


@app.get("/redfish/v1/", response_model=ServiceRoot)
def get_service_root():
    return ServiceRoot()


@app.get("/redfish/v1/Chassis")
def get_chassis_collection():
    return {
        "@odata.id": "/redfish/v1/Chassis",
        "@odata.type": "#ChassisCollection.ChassisCollection",
        "Name": "Chassis Collection",
        "Members@odata.count": 1,
        "Members": [{"@odata.id": "/redfish/v1/Chassis/1"}],
    }


@app.get("/redfish/v1/Chassis/1")
def get_chassis():
    return {
        "@odata.id": "/redfish/v1/Chassis/1",
        "@odata.type": "#Chassis.v1_22_0.Chassis",
        "Id": "1",
        "Name": "Liquid Cooled High-Density Rack Chassis",
        "ChassisType": "RackGroup",
        "ThermalSubsystem": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem"},
        "Sensors": {"@odata.id": "/redfish/v1/Chassis/1/Sensors"},
        "Status": {"State": "Enabled", "Health": simulator.health_status},
    }


@app.get("/redfish/v1/Chassis/1/ThermalSubsystem")
def get_thermal_subsystem():
    return {
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem",
        "@odata.type": "#ThermalSubsystem.v1_1_0.ThermalSubsystem",
        "Id": "ThermalSubsystem",
        "Name": "Chassis Thermal Subsystem",
        "CoolingLoops": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops"},
        "Status": {"State": "Enabled", "Health": simulator.health_status},
    }


@app.get("/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops")
def get_cooling_loops_collection():
    return {
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops",
        "@odata.type": "#CoolingLoopCollection.CoolingLoopCollection",
        "Name": "Cooling Loop Collection",
        "Members@odata.count": 1,
        "Members": [{"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1"}],
    }


@app.get("/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1")
def get_cooling_loop():
    state = simulator.tick()
    return CoolingLoopResource(
        **{
            "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1",
            "@odata.type": "#CoolingLoop.v1_0_0.CoolingLoop",
            "Id": "1",
            "Name": "Secondary Direct-to-Chip Cooling Loop",
            "CoolantType": "Water-Glycol",
            "Status": {"State": "Enabled", "Health": state["health_status"]},
            "SupplyTemperatureCelsius": state["supply_temperature_celsius"],
            "ReturnTemperatureCelsius": state["return_temperature_celsius"],
            "FlowRateLPM": state["flow_rate_lpm"],
            "PressurekPa": state["pressure_kpa"],
        }
    )


@app.get("/redfish/v1/Chassis/1/Sensors")
def get_sensors_collection():
    sensors = ["SupplyTemp", "ReturnTemp", "FlowRate", "Pressure", "PumpRPM"]
    members = [{"@odata.id": f"/redfish/v1/Chassis/1/Sensors/{s}"} for s in sensors]
    return {
        "@odata.id": "/redfish/v1/Chassis/1/Sensors",
        "@odata.type": "#SensorCollection.SensorCollection",
        "Name": "Sensor Collection",
        "Members@odata.count": len(members),
        "Members": members,
    }


@app.get("/redfish/v1/Chassis/1/Sensors/{sensor_id}")
def get_sensor(sensor_id: str):
    state = simulator.tick()

    sensor_map = {
        "SupplyTemp": ("Supply Fluid Temperature", state["supply_temperature_celsius"], "Cel"),
        "ReturnTemp": ("Return Fluid Temperature", state["return_temperature_celsius"], "Cel"),
        "FlowRate": ("Coolant Flow Rate", state["flow_rate_lpm"], "LPM"),
        "Pressure": ("Loop Pressure", state["pressure_kpa"], "kPa"),
        "PumpRPM": ("Primary Pump Speed", state["pump_rpm"], "RPM"),
    }

    if sensor_id not in sensor_map:
        raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' not found.")

    name, reading, units = sensor_map[sensor_id]

    return SensorReading(
        **{
            "@odata.id": f"/redfish/v1/Chassis/1/Sensors/{sensor_id}",
            "@odata.type": "#Sensor.v1_2_0.Sensor",
            "Id": sensor_id,
            "Name": name,
            "Reading": reading,
            "ReadingUnits": units,
            "Status": {"State": "Enabled", "Health": state["health_status"]},
        }
    )


@app.get("/redfish/v1/EventService")
def get_event_service():
    return {
        "@odata.id": "/redfish/v1/EventService",
        "@odata.type": "#EventService.v1_8_0.EventService",
        "Id": "EventService",
        "Name": "Redfish Event Service",
        "Status": {"State": "Enabled", "Health": "OK"},
        "SSEFilterPropertiesSupported": {"MetricReport": True, "Event": True},
        "ServerSentEventUri": "/redfish/v1/EventService/SSE",
    }


@app.get("/redfish/v1/TelemetryService/MetricReports/CoolingLoopMetrics")
def get_cooling_loop_metric_report():
    state = simulator.tick()
    return {
        "@odata.id": "/redfish/v1/TelemetryService/MetricReports/CoolingLoopMetrics",
        "@odata.type": "#MetricReport.v1_4_2.MetricReport",
        "Id": "CoolingLoopMetrics",
        "Name": "Cooling Loop Realtime Metric Report",
        "MetricValues": [
            {"MetricId": "SupplyTemp", "MetricValue": str(state["supply_temperature_celsius"])},
            {"MetricId": "ReturnTemp", "MetricValue": str(state["return_temperature_celsius"])},
            {"MetricId": "FlowRate", "MetricValue": str(state["flow_rate_lpm"])},
            {"MetricId": "Pressure", "MetricValue": str(state["pressure_kpa"])},
            {"MetricId": "PumpRPM", "MetricValue": str(state["pump_rpm"])},
        ],
    }


import json
import asyncio
from fastapi.responses import StreamingResponse


@app.get("/redfish/v1/EventService/SSE")
async def get_event_service_sse():
    """Server-Sent Events endpoint streaming Redfish telemetry events live."""

    async def event_generator():
        while True:
            state = simulator.tick()
            event_data = {
                "@odata.type": "#Event.v1_7_0.Event",
                "Id": "LiquidCoolingTelemetryEvent",
                "Events": [
                    {
                        "EventId": "TelemetryUpdate",
                        "EventType": "MetricReport",
                        "OriginOfCondition": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1"},
                        "Message": f"Supply: {state['supply_temperature_celsius']}C, Return: {state['return_temperature_celsius']}C, Flow: {state['flow_rate_lpm']}LPM",
                        "Severity": "OK" if state["health_status"] == "OK" else "Critical",
                    }
                ],
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

