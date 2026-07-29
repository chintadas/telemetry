from typing import List, Optional
from pydantic import BaseModel, Field


class ODataResource(BaseModel):
    odata_id: str = Field(..., alias="@odata.id")
    odata_type: str = Field(..., alias="@odata.type")
    id: str = Field(..., alias="Id")
    name: str = Field(..., alias="Name")


class ServiceRoot(BaseModel):
    odata_id: str = Field("/redfish/v1/", alias="@odata.id")
    odata_type: str = Field("#ServiceRoot.v1_13_0.ServiceRoot", alias="@odata.type")
    id: str = Field("RootService", alias="Id")
    name: str = Field("Root Service", alias="Name")
    redfish_version: str = Field("1.17.0", alias="RedfishVersion")
    chassis: dict = Field(default_factory=lambda: {"@odata.id": "/redfish/v1/Chassis"}, alias="Chassis")


class SensorReading(BaseModel):
    odata_id: str = Field(..., alias="@odata.id")
    odata_type: str = Field("#Sensor.v1_2_0.Sensor", alias="@odata.type")
    id: str = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    reading: float = Field(..., alias="Reading")
    reading_units: str = Field(..., alias="ReadingUnits")
    status: dict = Field(default_factory=lambda: {"State": "Enabled", "Health": "OK"}, alias="Status")


class CoolingLoopResource(BaseModel):
    odata_id: str = Field(..., alias="@odata.id")
    odata_type: str = Field("#CoolingLoop.v1_0_0.CoolingLoop", alias="@odata.type")
    id: str = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    coolant_type: str = Field("Water-Glycol", alias="CoolantType")
    status: dict = Field(default_factory=lambda: {"State": "Enabled", "Health": "OK"}, alias="Status")
    supply_temperature_celsius: float = Field(..., alias="SupplyTemperatureCelsius")
    return_temperature_celsius: float = Field(..., alias="ReturnTemperatureCelsius")
    flow_rate_lpm: float = Field(..., alias="FlowRateLPM")
    pressure_kpa: float = Field(..., alias="PressurekPa")
