
from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class EVType:
    name: str
    priority_weight: float  # smaller => higher priority

AMBULANCE = EVType("AMBULANCE", 0.8)
FIRE_TRUCK = EVType("FIRE_TRUCK", 1.0)
POLICE = EVType("POLICE", 1.1)

@dataclass
class EmergencyVehicle:
    vid: int
    ev_type: EVType
    approach: str           # 'N','E','S','W'
    distance_m: float
    speed_free: float
    speed_blocked: float
    detected: bool = False
    detection_time_s: Optional[float] = None
    passed: bool = False
    pass_time_s: Optional[float] = None
    meta: Dict = field(default_factory=dict)

@dataclass
class SignalState:
    phase: str              # 'NS' or 'EW'
    subphase: str           # 'GREEN' | 'YELLOW' | 'ALL_RED'
    time_in_state_s: float

@dataclass
class SimConfig:
    duration_s: float = 120.0
    dt_s: float = 0.5
    out_dir: str = "outputs"
