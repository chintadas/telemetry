# Mock Redfish Telemetry Engine - Liquid Cooling Loop

A lightweight, asynchronous mock telemetry engine simulating a data center liquid cooling loop (Coolant Distribution Unit - CDU, heat load, supply/return fluid temperatures, flow rate, pressure, and pump speed) conforming to DMTF Redfish standard schemas.

---

## Architecture Overview

```
                          ┌──────────────────────────┐
                          │  Cooling Loop Simulator   │
                          │   (Physics & Jitter)     │
                          └────────────┬─────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         │   FastAPI Redfish Server   │
                         └──────────────┬────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
  Redfish REST Endpoints      Server-Sent Events (SSE)     Simulation Control CLI
`/redfish/v1/Chassis/1/...` `/redfish/v1/EventService/SSE` `python3 src/cli/control.py`
```

---

## Features

- **Redfish Compliant REST API**: Serves `ServiceRoot`, `Chassis`, `ThermalSubsystem`, `CoolingLoop`, `SensorCollection`, and `MetricReport` resources with proper `@odata.id` and `@odata.type` annotations and `OData-Version: 4.0` headers.
- **Thermodynamic Physics Engine**: Calculates real-time temperature deltas based on heat load, coolant specific heat capacity, and fluid mass flow rate.
- **Live SSE Event Stream**: Streams real-time Redfish `MetricReport` event JSON payloads over Server-Sent Events (`/redfish/v1/EventService/SSE`).
- **CLI Fault Injection & Simulation Control**: Trigger simulated workload surges, pump speed adjustments, or fault scenarios (`pump_failure`, `leak`, `thermal_surge`).

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Mock Server
```bash
PYTHONPATH=. uvicorn src.server.app:app --reload --port 8000
```

---

## Redfish REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/redfish/v1/` | GET | Service Root |
| `/redfish/v1/Chassis/1` | GET | Rack Chassis details and status |
| `/redfish/v1/Chassis/1/ThermalSubsystem` | GET | Thermal subsystem resources |
| `/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1` | GET | Real-time liquid cooling loop metrics |
| `/redfish/v1/Chassis/1/Sensors` | GET | Sensor collection |
| `/redfish/v1/Chassis/1/Sensors/{SupplyTemp\|ReturnTemp\|FlowRate\|Pressure\|PumpRPM}` | GET | Individual sensor readings |
| `/redfish/v1/EventService` | GET | Event service root |
| `/redfish/v1/EventService/SSE` | GET | Server-Sent Events live stream |
| `/redfish/v1/TelemetryService/MetricReports/CoolingLoopMetrics` | GET | Consolidated metric report |

---

## Usage Examples

### Inspect Cooling Loop Telemetry
```bash
curl -s http://localhost:8000/redfish/v1/Chassis/1/ThermalSubsystem/CoolingLoops/1 | jq .
```

### Stream Live SSE Telemetry Events
```bash
curl -N http://localhost:8000/redfish/v1/EventService/SSE
```

### Inject Faults & Control Simulation via CLI

- **Adjust Heat Load (Watts)**:
  ```bash
  python3 src/cli/control.py heat-load 15000
  ```

- **Adjust Pump Speed (RPM)**:
  ```bash
  python3 src/cli/control.py pump-rpm 2000
  ```

- **Inject Fault Scenario**:
  ```bash
  python3 src/cli/control.py inject-fault leak
  ```

- **Reset Simulation State**:
  ```bash
  python3 src/cli/control.py reset
  ```

---

## Running Tests

Run the full automated test suite:
```bash
PYTHONPATH=. python3 -m unittest discover -s tests
```
