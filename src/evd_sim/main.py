
import argparse, os, sys, statistics, csv, random
from .types import SimConfig
from .sim import SimWorld

def summarize(world):
    passed = [e for e in world.evs if e.passed]
    det = [e for e in world.evs if e.detected]
    print(f"Mode: {world.mode} | Detector: {world.detector_mode}")
    print(f"EVs: {len(world.evs)}  Detected: {len(det)}/{len(world.evs)}  Passed: {len(passed)}/{len(world.evs)}")
    if passed:
        times = [e.pass_time_s for e in passed if e.pass_time_s is not None]
        print(f"Pass time (s): min={min(times):.1f}, median={statistics.median(times):.1f}, max={max(times):.1f}")

def init_inputs(inputs_dir: str, num_evs: int, duration_s: float, dt_s: float, seed: int = 42):
    """
    Tạo inputs/vision.csv và inputs/audio.csv:
    t,ev1,ev2,...,evN
    """
    os.makedirs(inputs_dir, exist_ok=True)
    vision_path = os.path.join(inputs_dir, "vision.csv")
    audio_path  = os.path.join(inputs_dir, "audio.csv")

    headers = ["t"] + [f"ev{i}" for i in range(1, num_evs + 1)]
    rng_v = random.Random(seed)
    rng_a = random.Random(seed + 1)

    def gen_row(t, rng, k):
        # tín hiệu tăng dần nhẹ theo thời gian + nhiễu nhỏ, clamp [0,1]
        base = 0.02 + 0.004 * t
        vals = []
        for i in range(k):
            noise = rng.uniform(-0.03, 0.03)
            v = max(0.0, min(1.0, base + (i * 0.01) + noise))
            vals.append(v)
        return [f"{t:.2f}"] + [f"{v:.3f}" for v in vals]

    with open(vision_path, "w", newline="") as fv, open(audio_path, "w", newline="") as fa:
        wv = csv.writer(fv); wa = csv.writer(fa)
        wv.writerow(headers); wa.writerow(headers)
        t = 0.0
        while t <= duration_s + 1e-9:
            row_v = gen_row(t, rng_v, num_evs)
            row_a = gen_row(t, rng_a, num_evs)
            # audio thường yếu hơn một chút
            row_a = [row_a[0]] + [f"{max(0.0, min(1.0, float(x)*0.8)):.3f}" for x in row_a[1:]]
            wv.writerow(row_v)
            wa.writerow(row_a)
            t += dt_s
    print(f"[OK] Created sample inputs:\n - {vision_path}\n - {audio_path}")

def main():
    ap = argparse.ArgumentParser(description="EVD-SIM v4 (input-first)")
    ap.add_argument("--mode", choices=["baseline","evd"], default="evd")
    ap.add_argument("--detector_mode", choices=["stub","playback","external"], default="stub")
    ap.add_argument("--num_evs", type=int, default=3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--duration_s", type=float, default=120.0)
    ap.add_argument("--dt_s", type=float, default=0.5)
    ap.add_argument("--inputs_dir", type=str, default="../inputs")
    ap.add_argument("--init-inputs", action="store_true", help="Generate sample inputs (vision.csv, audio.csv)")
    args = ap.parse_args()

    if args.init_inputs:
        init_inputs(args.inputs_dir, args.num_evs, args.duration_s, args.dt_s, seed=args.seed)
        return

    # Kiểm tra input khi chạy playback
    if args.detector_mode == "playback":
        v_csv = os.path.join(args.inputs_dir, "vision.csv")
        a_csv = os.path.join(args.inputs_dir, "audio.csv")
        if not os.path.exists(v_csv) or not os.path.exists(a_csv):
            print(f"[ERROR] playback mode requires {v_csv} and {a_csv}.", file=sys.stderr)
            print("Tip: run with --init-inputs to generate sample files.", file=sys.stderr)
            sys.exit(2)

    cfg = SimConfig(duration_s=args.duration_s, dt_s=args.dt_s)
    world = SimWorld(mode=args.mode, detector_mode=args.detector_mode,
                     num_evs=args.num_evs, seed=args.seed, cfg=cfg, inputs_dir=args.inputs_dir)
    csv_path = world.run()
    summarize(world)
    print("\nOutputs:")
    print(" -", os.path.abspath(csv_path))

if __name__ == "__main__":
    main()
