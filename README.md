
# EVD-SIM v4 — Input-first Emergency Vehicle Preemption Simulator

## TL;DR
```bash
cd evd_sim4/src

# A) Generate sample inputs (creates ../inputs/vision.csv & audio.csv)
python -m evd_sim.main --init-inputs

# B) Run with your inputs (playback)
python -m evd_sim.main --mode evd --detector_mode playback --num_evs 3 --duration_s 60 --dt_s 0.5

# C) Or run quick simulation (no inputs needed)
python -m evd_sim.main --mode evd --detector_mode stub --num_evs 3 --seed 7
```

Outputs are written to `src/outputs/timeline.csv`.
