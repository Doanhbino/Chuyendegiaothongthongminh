
import os, csv, random
from typing import List, Literal
from .types import SimConfig, EmergencyVehicle, AMBULANCE, FIRE_TRUCK, POLICE
from .providers import VisionStub, AudioStub, PlaybackById, ExternalVision, ExternalAudio
from .fusion import fused_trigger
from .scheduler import SJFScheduler
from .controller import SignalController, SignalConfig

class SimWorld:
    def __init__(self, mode: Literal["baseline","evd"]="evd",
                 detector_mode: Literal["stub","playback","external"]="stub",
                 num_evs=3, seed=7, cfg: SimConfig = None, inputs_dir: str = "../inputs"):
        random.seed(seed)
        self.cfg = cfg or SimConfig()
        self.mode = mode
        self.detector_mode = detector_mode
        self.time_s = 0.0
        self.inputs_dir = inputs_dir

        self.controller = SignalController(SignalConfig())
        self.scheduler = SJFScheduler(traffic_density={"N":1.2,"E":1.0,"S":1.3,"W":0.9})

        self.evs: List[EmergencyVehicle] = self._random_evs(num_evs)
        self.timeline = []

        if detector_mode == "stub":
            self.vision = VisionStub(); self.audio = AudioStub()
            self.playback_v = None; self.playback_a = None
        elif detector_mode == "playback":
            v_csv = os.path.join(inputs_dir, "vision.csv")
            a_csv = os.path.join(inputs_dir, "audio.csv")
            self.playback_v = PlaybackById(v_csv)
            self.playback_a = PlaybackById(a_csv)
            self.vision = None; self.audio = None
        elif detector_mode == "external":
            self.vision = ExternalVision(); self.audio = ExternalAudio()
            self.playback_v = None; self.playback_a = None
        else:
            raise ValueError("Unknown detector_mode")

    def _random_evs(self, n):
        types = [AMBULANCE, FIRE_TRUCK, POLICE]
        dirs = ["N","E","S","W"]
        evs = []
        for i in range(n):
            evs.append(EmergencyVehicle(
                vid=i+1,
                ev_type=random.choice(types),
                approach=random.choice(dirs),
                distance_m=random.uniform(280, 600),
                speed_free=random.uniform(12, 18),
                speed_blocked=random.uniform(1.5, 3.0),
            ))
        return evs

    def _log_row(self):
        row = {
            "t": round(self.time_s,2),
            "phase": self.controller.state.phase,
            "subphase": self.controller.state.subphase,
            "evs_active": sum(1 for e in self.evs if not e.passed),
        }
        for e in self.evs:
            row[f"ev{e.vid}_d"] = round(e.distance_m,1)
            row[f"ev{e.vid}_det"] = int(e.detected)
            row[f"ev{e.vid}_passed"] = int(e.passed)
        self.timeline.append(row)

    def _tick(self):
        for e in self.evs:
            if not e.detected and not e.passed:
                if self.detector_mode == "stub":
                    pv = self.vision.detect(e.distance_m, self.time_s, e.vid)
                    pa = self.audio.detect(e.distance_m, self.time_s, e.vid)
                elif self.detector_mode == "playback":
                    pv = self.playback_v.detect(e.distance_m, self.time_s, e.vid)
                    pa = self.playback_a.detect(e.distance_m, self.time_s, e.vid)
                else:  # external
                    pv = self.vision.detect(e.distance_m, self.time_s, e.vid)
                    pa = self.audio.detect(e.distance_m, self.time_s, e.vid)
                pf, trig = fused_trigger(pv, pa)
                if trig:
                    e.detected = True
                    e.detection_time_s = self.time_s

        if self.mode == "evd":
            active = [e for e in self.evs if e.detected and not e.passed]
            pick = self.scheduler.pick(active) if active else None
            if pick:
                self.controller.request_phase_for_ev(pick)

        self.controller.step(self.cfg.dt_s, ev_mode=(self.mode=="evd"))

        greens = self.controller.current_green_approaches()
        for e in self.evs:
            if e.passed: continue
            v = e.speed_free if e.approach in greens else e.speed_blocked
            e.distance_m = max(0.0, e.distance_m - v*self.cfg.dt_s)
            if e.distance_m <= 0.0 and not e.passed:
                e.passed = True
                e.pass_time_s = self.time_s

        self._log_row()

    def run(self):
        os.makedirs(self.cfg.out_dir, exist_ok=True)
        while self.time_s <= self.cfg.duration_s:
            self._tick()
            self.time_s += self.cfg.dt_s
        if not self.timeline:
            raise RuntimeError("No timeline generated.")
        csv_path = os.path.join(self.cfg.out_dir, "timeline.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.timeline[0].keys()))
            writer.writeheader()
            for r in self.timeline:
                writer.writerow(r)
        return csv_path
