
def noisy_or(pv: float, pa: float) -> float:
    return 1.0 - (1.0 - pv) * (1.0 - pa)

def fused_trigger(pv: float, pa: float, t_v=0.55, t_a=0.60, t_f=0.60) -> tuple[float, bool]:
    pf = noisy_or(pv, pa)
    trig = (pv >= t_v) or (pa >= t_a) or (pf >= t_f)
    return pf, trig
