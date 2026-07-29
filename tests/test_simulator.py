"""
Tests for CoolingLoopSimulator.
"""

import unittest
from src.engine.simulator import CoolingLoopSimulator


class TestCoolingLoopSimulator(unittest.TestCase):

    def setUp(self):
        self.sim = CoolingLoopSimulator(
            loop_id="Loop1",
            supply_temp_celsius=20.0,
            flow_rate_lpm=40.0,
            heat_load_watts=10000.0,
            pump_rpm=3000.0,
            pressure_kpa=220.0,
        )

    def test_initial_state_calculation(self):
        # 10,000 W / ((40/60 kg/s) * 4000 J/kgC) = 10000 / 2666.67 = 3.75 C delta
        return_temp = self.sim.calculate_return_temperature()
        self.assertAlmostEqual(return_temp, 23.75, delta=0.1)

    def test_heat_load_change(self):
        self.sim.set_heat_load(20000.0)  # Double heat load
        return_temp = self.sim.calculate_return_temperature()
        self.assertAlmostEqual(return_temp, 27.5, delta=0.1)

    def test_pump_speed_adjustment(self):
        self.sim.set_pump_rpm(1500.0)  # Half RPM -> half flow rate (20 LPM)
        self.assertEqual(self.sim.flow_rate, 20.0)
        self.assertEqual(self.sim.pressure_kpa, 110.0)

    def test_fault_injection_pump_failure(self):
        self.sim.inject_fault("pump_failure")
        self.assertEqual(self.sim.health_status, "Critical")
        self.assertEqual(self.sim.active_fault, "pump_failure")
        self.assertLessEqual(self.sim.flow_rate, 5.0)

    def test_clear_fault(self):
        self.sim.inject_fault("leak")
        self.assertEqual(self.sim.health_status, "Warning")
        self.sim.clear_fault()
        self.assertEqual(self.sim.health_status, "OK")
        self.assertIsNone(self.sim.active_fault)

    def test_tick_returns_state_dict(self):
        state = self.sim.tick(noise=False)
        self.assertEqual(state["loop_id"], "Loop1")
        self.assertEqual(state["supply_temperature_celsius"], 20.0)
        self.assertGreater(state["return_temperature_celsius"], 20.0)


if __name__ == "__main__":
    unittest.main()
