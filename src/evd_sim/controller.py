
from dataclasses import dataclass
from typing import Optional
from .types import SignalState, EmergencyVehicle

@dataclass
class SignalConfig:
    yellow_s: float = 3.0
    all_red_s: float = 1.0
    default_cycle_green_s: float = 30.0

class SignalController:
    def __init__(self, cfg: SignalConfig):
        self.cfg = cfg
        self.state = SignalState(phase="NS", subphase="GREEN", time_in_state_s=0.0)
        self._queued_phase: Optional[str] = None

    def current_green_approaches(self):
        return ("N","S") if self.state.phase=="NS" else ("E","W")

    def request_phase_for_ev(self, ev: EmergencyVehicle):
        desired = "NS" if ev.approach in ("N","S") else "EW"
        if desired != self.state.phase and self.state.subphase=="GREEN":
            self.state = SignalState(phase=self.state.phase, subphase="YELLOW", time_in_state_s=0.0)
            self._queued_phase = desired

    def step(self, dt: float, ev_mode: bool):
        s = self.state
        s.time_in_state_s += dt
        if s.subphase=="GREEN":
            if not ev_mode and s.time_in_state_s >= self.cfg.default_cycle_green_s:
                self.state = SignalState(s.phase, "YELLOW", 0.0)
                self._queued_phase = "EW" if s.phase=="NS" else "NS"
        elif s.subphase=="YELLOW":
            if s.time_in_state_s >= self.cfg.yellow_s:
                self.state = SignalState(s.phase, "ALL_RED", 0.0)
        elif s.subphase=="ALL_RED":
            if s.time_in_state_s >= self.cfg.all_red_s:
                new_phase = self._queued_phase or ("EW" if s.phase=="NS" else "NS")
                self.state = SignalState(new_phase, "GREEN", 0.0)
                self._queued_phase = None
