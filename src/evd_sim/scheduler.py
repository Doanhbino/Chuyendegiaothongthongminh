
from typing import Dict, List, Optional
from .types import EmergencyVehicle

class SJFScheduler:
    def __init__(self, traffic_density: Dict[str,float], min_speed=6.0):
        self.traffic_density = traffic_density
        self.min_speed = min_speed

    def cost(self, ev: EmergencyVehicle) -> float:
        speed_est = max(self.min_speed, 0.6 * ev.speed_free)
        eta = ev.distance_m / speed_est
        density = self.traffic_density.get(ev.approach, 1.0)
        return eta * density + ev.ev_type.priority_weight

    def pick(self, evs: List[EmergencyVehicle]) -> Optional[EmergencyVehicle]:
        alive = [e for e in evs if not e.passed]
        return min(alive, key=self.cost) if alive else None
