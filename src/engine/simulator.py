"""
Liquid Cooling Loop Simulator.
Simulates thermodynamic heat exchange, fluid flow, and pressure dynamics for a server cooling loop.
"""

import random
from typing import Dict, Any


class CoolingLoopSimulator:
    def __init__(
        self,
        loop_id: str = "Loop1",
        supply_temp_celsius: float = 20.0,
        flow_rate_lpm: float = 40.0,
        heat_load_watts: float = 10000.0,
        pump_rpm: float = 3000.0,
        pressure_kpa: float = 220.0,
    ):
        self.loop_id = loop_id
        self.supply_temp = supply_temp_celsius
        self.flow_rate = flow_rate_lpm
        self.heat_load = heat_load_watts
        self.pump_rpm = pump_rpm
        self.pressure_kpa = pressure_kpa
        self.health_status = "OK"
        self.active_fault: str = None

        # Thermal capacity constant for coolant (Water-Glycol mix ~4000 J/(kg*C))
        self.specific_heat = 4000.0
        self.fluid_density = 1.0  # kg/L

    def calculate_return_temperature(self) -> float:
        """
        Calculates return fluid temperature based on heat load and mass flow rate:
        Delta_T = Heat_Load_Watts / (Mass_Flow_kg_sec * Specific_Heat)
        """
        if self.flow_rate <= 0.1:
            # Stagnant fluid leads to heat accumulation
            return self.supply_temp + (self.heat_load / 500.0)

        mass_flow_kg_sec = (self.flow_rate / 60.0) * self.fluid_density
        delta_t = self.heat_load / (mass_flow_kg_sec * self.specific_heat)
        return round(self.supply_temp + delta_t, 2)

    def set_heat_load(self, watts: float):
        """Update active heat load in Watts (e.g. server CPU/GPU workload)."""
        self.heat_load = max(0.0, watts)

    def set_pump_rpm(self, rpm: float):
        """Update pump RPM, which proportionally adjusts flow rate and pressure."""
        self.pump_rpm = max(0.0, rpm)
        # Flow rate scales linearly with pump RPM (3000 RPM -> nominal 40 LPM)
        self.flow_rate = round((self.pump_rpm / 3000.0) * 40.0, 2)
        self.pressure_kpa = round((self.pump_rpm / 3000.0) * 220.0, 2)

    def inject_fault(self, fault_type: str):
        """Inject synthetic fault scenario."""
        self.active_fault = fault_type
        if fault_type == "pump_failure":
            self.set_pump_rpm(300.0)  # Sudden drop in pump speed
            self.health_status = "Critical"
        elif fault_type == "leak":
            self.pressure_kpa = 50.0  # Severe pressure drop
            self.health_status = "Warning"
        elif fault_type == "thermal_surge":
            self.heat_load = 25000.0  # 2.5x heat surge
            self.health_status = "Warning"

    def clear_fault(self):
        """Clear active fault scenario."""
        self.active_fault = None
        self.health_status = "OK"
        self.set_pump_rpm(3000.0)
        self.set_heat_load(10000.0)

    def tick(self, noise: bool = True) -> Dict[str, Any]:
        """
        Advance simulation state by 1 tick.
        Optionally add realistic subtle sensor noise.
        """
        supply_jitter = random.gauss(0, 0.05) if noise else 0.0
        flow_jitter = random.gauss(0, 0.1) if noise else 0.0
        pressure_jitter = random.gauss(0, 0.5) if noise else 0.0

        current_supply = round(self.supply_temp + supply_jitter, 2)
        current_flow = max(0.0, round(self.flow_rate + flow_jitter, 2))
        current_pressure = max(0.0, round(self.pressure_kpa + pressure_jitter, 2))

        # Recalculate return temp with current supply & flow
        if current_flow > 0.1:
            mass_flow = (current_flow / 60.0) * self.fluid_density
            delta_t = self.heat_load / (mass_flow * self.specific_heat)
            current_return = round(current_supply + delta_t, 2)
        else:
            current_return = round(current_supply + 50.0, 2)

        return {
            "loop_id": self.loop_id,
            "health_status": self.health_status,
            "active_fault": self.active_fault,
            "supply_temperature_celsius": current_supply,
            "return_temperature_celsius": current_return,
            "delta_t_celsius": round(current_return - current_supply, 2),
            "flow_rate_lpm": current_flow,
            "pressure_kpa": current_pressure,
            "pump_rpm": self.pump_rpm,
            "heat_load_watts": self.heat_load,
        }
