
import math, random, csv, bisect, os
from typing import Dict, List, Tuple, Optional

class BaseDetector:
    def detect(self, distance_m: float, t_now: Optional[float] = None, vid: Optional[int] = None) -> float:
        raise NotImplementedError

class VisionStub(BaseDetector):
    def __init__(self, base=0.9, d0=140.0, noise=0.08):
        self.base, self.d0, self.noise = base, d0, noise
    def detect(self, d, t_now=None, vid=None):
        c = self.base * math.exp(-(d/self.d0)**2) + random.gauss(0, self.noise)
        return max(0.0, min(1.0, c))

class AudioStub(BaseDetector):
    def __init__(self, base=0.85, d0=320.0, noise=0.12):
        self.base, self.d0, self.noise = base, d0, noise
    def detect(self, d, t_now=None, vid=None):
        c = self.base * math.exp(-(d/self.d0)**2) + random.gauss(0, self.noise)
        return max(0.0, min(1.0, c))

class ExternalVision(BaseDetector):
    def __init__(self): self.last_conf = 0.0
    def update(self, conf: float): self.last_conf = max(0.0, min(1.0, float(conf)))
    def detect(self, d, t_now=None, vid=None): return self.last_conf

class ExternalAudio(BaseDetector):
    def __init__(self): self.last_conf = 0.0
    def update(self, conf: float): self.last_conf = max(0.0, min(1.0, float(conf)))
    def detect(self, d, t_now=None, vid=None): return self.last_conf

class PlaybackById(BaseDetector):
    """Read CSV with columns: t,ev1,ev2,... and return conf(t_now, vid)."""
    def __init__(self, path_csv: str):
        if not os.path.exists(path_csv):
            raise FileNotFoundError(f"Input CSV not found: {path_csv}")
        rows = []
        with open(path_csv, newline='') as f:
            for r in csv.DictReader(f):
                rows.append({k:(float(v) if v!='' else 0.0) for k,v in r.items()})
        self.data: Dict[int, Tuple[List[float], List[float]]] = {}
        for r in rows:
            t = r.get("t", 0.0)
            for k,v in r.items():
                if k=='t': continue
                if k.startswith('ev'):
                    vid = int(k[2:])
                    self.data.setdefault(vid, ([], []))
                    self.data[vid][0].append(t)
                    self.data[vid][1].append(v)
    def detect(self, d, t_now=None, vid=None):
        if vid is None or t_now is None: return 0.0
        if vid not in self.data: return 0.0
        ts, vs = self.data[vid]
        i = bisect.bisect_right(ts, t_now) - 1
        return 0.0 if i < 0 else max(0.0, min(1.0, vs[i]))
