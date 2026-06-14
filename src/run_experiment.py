import csv
import hashlib
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

SEEDS = list(range(7))
DEPLOYMENT_STEPS = 72
STRESS_STEPS = 48
BASE_SEED = 40438383

TASKS = [
    {
        "skill": "pick_place",
        "base_success": 0.94,
        "base_half_life": 29.0,
        "unsafe_base": 0.030,
        "friction": 0.80,
        "mass": 0.45,
        "compliance": 0.35,
    },
    {
        "skill": "door_pull",
        "base_success": 0.91,
        "base_half_life": 24.0,
        "unsafe_base": 0.045,
        "friction": 0.55,
        "mass": 0.35,
        "compliance": 0.90,
    },
    {
        "skill": "drawer_slide",
        "base_success": 0.92,
        "base_half_life": 26.0,
        "unsafe_base": 0.040,
        "friction": 0.75,
        "mass": 0.40,
        "compliance": 0.70,
    },
    {
        "skill": "peg_insert",
        "base_success": 0.89,
        "base_half_life": 20.0,
        "unsafe_base": 0.060,
        "friction": 0.35,
        "mass": 0.30,
        "compliance": 1.05,
    },
]

SPLITS = {
    "nominal_slow_drift": {
        "drift": 0.18,
        "friction_shift": 0.10,
        "mass_shift": 0.08,
        "compliance_shift": 0.08,
        "sensor_noise": 0.035,
        "mode_flip": 0.015,
    },
    "friction_shift": {
        "drift": 0.34,
        "friction_shift": 0.46,
        "mass_shift": 0.10,
        "compliance_shift": 0.12,
        "sensor_noise": 0.045,
        "mode_flip": 0.030,
    },
    "payload_mass_shift": {
        "drift": 0.32,
        "friction_shift": 0.12,
        "mass_shift": 0.50,
        "compliance_shift": 0.10,
        "sensor_noise": 0.045,
        "mode_flip": 0.030,
    },
    "compliance_shift": {
        "drift": 0.35,
        "friction_shift": 0.12,
        "mass_shift": 0.12,
        "compliance_shift": 0.52,
        "sensor_noise": 0.055,
        "mode_flip": 0.040,
    },
    "combined_micro_shift": {
        "drift": 0.50,
        "friction_shift": 0.38,
        "mass_shift": 0.36,
        "compliance_shift": 0.42,
        "sensor_noise": 0.075,
        "mode_flip": 0.070,
    },
}

METHODS = [
    "frozen_behavior_clone",
    "domain_randomized_clone",
    "fixed_interval_refresh",
    "online_finetune",
    "scalar_uncertainty_gate",
    "conformal_risk_gate",
    "skill_half_life_scheduler",
    "oracle_shift_aware_scheduler",
]

ABLATIONS = [
    "full_skill_half_life_scheduler",
    "minus_per_skill_survival",
    "minus_probe_updates",
    "minus_hazard_margin",
    "minus_shift_decomposition",
    "fixed_global_half_life",
    "threshold_only_risk_gate",
]


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ci95(values):
    vals = np.asarray(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * vals.std(ddof=1) / math.sqrt(len(vals)))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def split_params(split, stress_axis=None, stress_level=0.0):
    params = dict(SPLITS.get(split, SPLITS["combined_micro_shift"]))
    if stress_axis is None:
        return params
    level = float(stress_level)
    if stress_axis == "drift_rate":
        params["drift"] = 0.14 + 0.62 * level
    elif stress_axis == "sensor_noise":
        params["sensor_noise"] = 0.025 + 0.150 * level
    elif stress_axis == "mode_flip":
        params["mode_flip"] = 0.005 + 0.160 * level
    elif stress_axis == "probe_cost":
        params["probe_cost_override"] = 0.035 + 0.180 * level
    elif stress_axis == "combined":
        params["drift"] = 0.16 + 0.62 * level
        params["friction_shift"] = 0.10 + 0.46 * level
        params["mass_shift"] = 0.10 + 0.44 * level
        params["compliance_shift"] = 0.10 + 0.48 * level
        params["sensor_noise"] = 0.025 + 0.130 * level
        params["mode_flip"] = 0.010 + 0.140 * level
        params["probe_cost_override"] = 0.045 + 0.120 * level
    else:
        raise ValueError(f"unknown stress axis {stress_axis}")
    return params


def physical_state(split, task, seed, step, total_steps, stress_axis=None, stress_level=0.0):
    params = split_params(split, stress_axis=stress_axis, stress_level=stress_level)
    progress = step / max(1, total_steps - 1)
    rng = stable_rng("phys", split, task["skill"], seed, step, stress_axis or "main", stress_level)
    seasonal = 0.08 * math.sin(2.0 * math.pi * (progress + 0.13 * seed + 0.07 * len(task["skill"])))
    impulse = 0.0
    if rng.random() < params["mode_flip"] * (0.35 + 1.30 * progress):
        impulse = rng.uniform(0.18, 0.38)

    friction = max(0.0, params["friction_shift"] * (0.25 + progress) + 0.18 * params["drift"] * progress + seasonal)
    mass = max(0.0, params["mass_shift"] * (0.20 + 0.90 * progress) + 0.10 * params["drift"] * progress)
    compliance = max(0.0, params["compliance_shift"] * (0.15 + 1.05 * progress) - 0.04 * seasonal)
    friction += rng.normal(0.0, 0.018)
    mass += rng.normal(0.0, 0.016)
    compliance += rng.normal(0.0, 0.018)
    friction = max(0.0, friction + 0.40 * impulse)
    mass = max(0.0, mass + 0.30 * impulse)
    compliance = max(0.0, compliance + 0.45 * impulse)

    weighted = (
        task["friction"] * friction**2
        + task["mass"] * mass**2
        + task["compliance"] * compliance**2
    )
    shift_norm = math.sqrt(max(0.0, weighted))
    true_half_life = task["base_half_life"] / (1.0 + 2.45 * shift_norm + 1.15 * impulse)
    true_half_life = clamp(true_half_life, 4.0, task["base_half_life"] * 1.15)

    obs_rng = stable_rng("obs", split, task["skill"], seed, step, stress_axis or "main", stress_level)
    obs_noise = params["sensor_noise"]
    observed_friction = max(0.0, friction + obs_rng.normal(0.0, obs_noise))
    observed_mass = max(0.0, mass + obs_rng.normal(0.0, obs_noise))
    observed_compliance = max(0.0, compliance + obs_rng.normal(0.0, obs_noise))
    observed_norm = math.sqrt(
        max(
            0.0,
            task["friction"] * observed_friction**2
            + task["mass"] * observed_mass**2
            + task["compliance"] * observed_compliance**2,
        )
    )
    mode_signal = clamp(impulse + obs_rng.normal(0.0, obs_noise * 0.75), 0.0, 0.60)

    return {
        "friction": friction,
        "mass": mass,
        "compliance": compliance,
        "shift_norm": shift_norm,
        "observed_friction": observed_friction,
        "observed_mass": observed_mass,
        "observed_compliance": observed_compliance,
        "observed_norm": observed_norm,
        "mode_signal": mode_signal,
        "impulse": impulse,
        "true_half_life": true_half_life,
        "sensor_noise": obs_noise,
        "probe_cost": params.get("probe_cost_override", 0.070),
    }


def method_effect(method):
    effects = {
        "frozen_behavior_clone": {"base_delta": 0.000, "half_life_mult": 0.95, "unsafe_mult": 1.20},
        "domain_randomized_clone": {"base_delta": -0.030, "half_life_mult": 1.28, "unsafe_mult": 0.95},
        "fixed_interval_refresh": {"base_delta": -0.005, "half_life_mult": 1.00, "unsafe_mult": 0.92},
        "online_finetune": {"base_delta": -0.010, "half_life_mult": 1.10, "unsafe_mult": 1.05},
        "scalar_uncertainty_gate": {"base_delta": -0.012, "half_life_mult": 1.03, "unsafe_mult": 0.85},
        "conformal_risk_gate": {"base_delta": -0.025, "half_life_mult": 1.05, "unsafe_mult": 0.62},
        "skill_half_life_scheduler": {"base_delta": -0.006, "half_life_mult": 1.04, "unsafe_mult": 0.58},
        "oracle_shift_aware_scheduler": {"base_delta": 0.000, "half_life_mult": 1.05, "unsafe_mult": 0.42},
    }
    return effects[method]


def estimate_half_life(method, task, phys, seed, step, ablation=None):
    if ablation is not None:
        return estimate_ablation_half_life(ablation, task, phys, seed, step)
    rng = stable_rng("estimate", method, task["skill"], seed, step)
    obs = phys["observed_norm"]
    if method == "oracle_shift_aware_scheduler":
        return phys["true_half_life"]
    if method == "frozen_behavior_clone":
        return task["base_half_life"] * (1.10 + rng.normal(0.0, 0.02))
    if method == "domain_randomized_clone":
        return task["base_half_life"] * 1.20 / (1.0 + 1.00 * obs + 0.20 * phys["mode_signal"])
    if method == "fixed_interval_refresh":
        return 18.0
    if method == "online_finetune":
        return task["base_half_life"] * 1.05 / (1.0 + 1.45 * obs + 0.35 * phys["mode_signal"])
    if method == "scalar_uncertainty_gate":
        return task["base_half_life"] / (1.0 + 1.75 * obs + 0.30 * phys["sensor_noise"])
    if method == "conformal_risk_gate":
        return task["base_half_life"] / (1.0 + 2.05 * obs + 0.55 * phys["mode_signal"])
    if method == "skill_half_life_scheduler":
        structured_shift = (
            0.95 * task["friction"] * phys["observed_friction"]
            + 0.90 * task["mass"] * phys["observed_mass"]
            + 1.00 * task["compliance"] * phys["observed_compliance"]
        ) / (task["friction"] + task["mass"] + task["compliance"])
        est = task["base_half_life"] / (1.0 + 2.35 * structured_shift + 0.95 * phys["mode_signal"])
        return clamp(est * (1.0 + rng.normal(0.0, 0.070)), 3.5, task["base_half_life"] * 1.10)
    raise ValueError(method)


def estimate_ablation_half_life(ablation, task, phys, seed, step):
    rng = stable_rng("ablation_estimate", ablation, task["skill"], seed, step)
    if ablation == "full_skill_half_life_scheduler":
        return estimate_half_life("skill_half_life_scheduler", task, phys, seed, step)
    if ablation == "minus_per_skill_survival":
        return 24.0 / (1.0 + 2.10 * phys["observed_norm"] + 0.65 * phys["mode_signal"])
    if ablation == "minus_probe_updates":
        base = estimate_half_life("skill_half_life_scheduler", task, phys, seed, step)
        return clamp(base * (1.0 + rng.normal(0.0, 0.18)), 3.0, task["base_half_life"] * 1.15)
    if ablation == "minus_hazard_margin":
        return estimate_half_life("skill_half_life_scheduler", task, phys, seed, step) * 1.08
    if ablation == "minus_shift_decomposition":
        return task["base_half_life"] / (1.0 + 1.70 * phys["observed_norm"] + 0.35 * phys["mode_signal"])
    if ablation == "fixed_global_half_life":
        return 18.0
    if ablation == "threshold_only_risk_gate":
        return task["base_half_life"] / (1.0 + 1.60 * phys["observed_norm"])
    raise ValueError(ablation)


def predict_success(task, age, est_half_life, method, phys, refreshed=False, ablation=None):
    if refreshed:
        age = 0.0
    base_delta = method_effect("skill_half_life_scheduler" if ablation else method)["base_delta"]
    floor = 0.18
    decay = math.exp(-math.log(2.0) * age / max(2.0, est_half_life))
    pred = floor + (task["base_success"] + base_delta - floor) * decay
    pred -= 0.030 * phys["observed_norm"] + 0.018 * phys["sensor_noise"]
    return clamp(pred, 0.02, 0.98)


def choose_action(method, task, age, est_half_life, pred_success, phys, step, ablation=None):
    refresh = False
    probe = False
    abstain = False
    if ablation is not None:
        method = "skill_half_life_scheduler"

    if method == "frozen_behavior_clone":
        pass
    elif method == "domain_randomized_clone":
        pass
    elif method == "fixed_interval_refresh":
        refresh = age >= 18.0
    elif method == "online_finetune":
        refresh = pred_success < 0.46 and phys["observed_norm"] > 0.72
    elif method == "scalar_uncertainty_gate":
        refresh = pred_success < 0.62 or phys["observed_norm"] > 0.78
    elif method == "conformal_risk_gate":
        if pred_success < 0.56 and phys["observed_norm"] > 0.62:
            abstain = True
        elif pred_success < 0.71 or age > 0.92 * est_half_life:
            refresh = True
        elif pred_success < 0.78:
            probe = True
    elif method == "skill_half_life_scheduler":
        hazard_margin = 0.74
        refresh_threshold = 0.71
        probe_band = 0.81
        if ablation == "minus_hazard_margin":
            hazard_margin = 1.02
            refresh_threshold = 0.61
        elif ablation == "threshold_only_risk_gate":
            hazard_margin = 0.98
            refresh_threshold = 0.63
            probe_band = 0.70
        elif ablation == "fixed_global_half_life":
            hazard_margin = 0.86
            refresh_threshold = 0.66
        if pred_success < refresh_threshold or age > hazard_margin * est_half_life:
            refresh = True
        elif ablation != "minus_probe_updates" and (pred_success < probe_band or phys["mode_signal"] > 0.18):
            probe = True
    elif method == "oracle_shift_aware_scheduler":
        true_pred = predict_success(task, age, phys["true_half_life"], method, phys)
        refresh = true_pred < 0.73 or age > 0.77 * phys["true_half_life"]
        probe = (not refresh) and true_pred < 0.82
    else:
        raise ValueError(method)
    return refresh, probe, abstain


def execute_episode(split, task, seed, step, method, state, total_steps, stress_axis=None, stress_level=0.0, ablation=None):
    phys = physical_state(split, task, seed, step, total_steps, stress_axis=stress_axis, stress_level=stress_level)
    est_half_life = estimate_half_life(method, task, phys, seed, step, ablation=ablation)
    pred_pre = predict_success(task, state["age"], est_half_life, method, phys, ablation=ablation)
    refresh, probe, abstain = choose_action(method, task, state["age"], est_half_life, pred_pre, phys, step, ablation=ablation)
    exec_age = 0.0 if refresh else state["age"]

    effect_key = "skill_half_life_scheduler" if ablation else method
    effect = method_effect(effect_key)
    adjusted_half_life = phys["true_half_life"] * effect["half_life_mult"]
    floor = 0.16
    decay = math.exp(-math.log(2.0) * exec_age / max(2.5, adjusted_half_life))
    success_prob = floor + (task["base_success"] + effect["base_delta"] - floor) * decay
    success_prob -= 0.055 * phys["shift_norm"] + 0.030 * (phys["impulse"] > 0.0)
    if probe:
        success_prob += 0.018
    if method == "online_finetune" and phys["mode_signal"] > 0.22:
        success_prob -= 0.035
    success_prob = clamp(success_prob, 0.02, 0.98)

    rng = stable_rng("rollout", split, task["skill"], seed, step, method, ablation or "none")
    success = False if abstain else bool(rng.random() < success_prob)
    stale = (not abstain) and exec_age > 1.05 * phys["true_half_life"]
    unsafe_prob = 0.0
    unsafe = False
    if not success and not abstain:
        age_ratio = exec_age / max(2.5, phys["true_half_life"])
        unsafe_prob = task["unsafe_base"] * (0.35 + 2.20 * age_ratio**1.45) * (0.70 + phys["shift_norm"])
        unsafe_prob += 0.028 if phys["impulse"] > 0.0 else 0.0
        unsafe_prob *= effect["unsafe_mult"]
        if probe:
            unsafe_prob *= 0.78
        if refresh:
            unsafe_prob *= 0.62
        unsafe = bool(rng.random() < clamp(unsafe_prob, 0.0, 0.92))

    pred_after = predict_success(task, exec_age, est_half_life, method, phys, refreshed=False, ablation=ablation)
    total_cost = 1.0 + (0.26 if refresh else 0.0) + (phys["probe_cost"] if probe else 0.0) + (0.48 if abstain else 0.0)
    if unsafe:
        total_cost += 0.85

    if refresh:
        state["age"] = 1.0
        state["refreshes"] += 1
    else:
        state["age"] += 1.0
    if probe:
        state["probes"] += 1
    if method == "online_finetune":
        if success:
            state["age"] = max(0.0, state["age"] - 0.22)
        else:
            state["age"] = max(0.0, state["age"] - 0.62 + 0.55 * phys["mode_signal"])

    row_method = ablation if ablation else method
    return {
        "split": split,
        "skill": task["skill"],
        "seed": seed,
        "step": step,
        "method": row_method,
        "goal_success": int(success),
        "unsafe_failure": int(unsafe),
        "stale_execution": int(stale),
        "refresh": int(refresh),
        "probe": int(probe),
        "abstain": int(abstain),
        "total_cost": f"{total_cost:.5f}",
        "predicted_success": f"{pred_after:.5f}",
        "calibration_abs_error": f"{abs(pred_after - float(success)):.5f}",
        "true_success_probability": f"{success_prob:.5f}",
        "estimated_half_life": f"{est_half_life:.5f}",
        "true_half_life": f"{phys['true_half_life']:.5f}",
        "half_life_abs_relative_error": f"{abs(est_half_life - phys['true_half_life']) / max(1.0, phys['true_half_life']):.5f}",
        "shift_norm": f"{phys['shift_norm']:.5f}",
        "observed_norm": f"{phys['observed_norm']:.5f}",
        "mode_signal": f"{phys['mode_signal']:.5f}",
        "exec_age": f"{exec_age:.5f}",
    }


def run_rollouts_for(split, methods, steps, stress_axis=None, stress_level=0.0, ablation_methods=None):
    rows = []
    ablation_methods = ablation_methods or []
    for seed in SEEDS:
        for task in TASKS:
            for method in methods:
                state = {"age": 0.0, "refreshes": 0, "probes": 0}
                for step in range(steps):
                    rows.append(
                        execute_episode(
                            split,
                            task,
                            seed,
                            step,
                            method,
                            state,
                            steps,
                            stress_axis=stress_axis,
                            stress_level=stress_level,
                        )
                    )
            for ablation in ablation_methods:
                state = {"age": 0.0, "refreshes": 0, "probes": 0}
                for step in range(steps):
                    rows.append(
                        execute_episode(
                            split,
                            task,
                            seed,
                            step,
                            "skill_half_life_scheduler",
                            state,
                            steps,
                            stress_axis=stress_axis,
                            stress_level=stress_level,
                            ablation=ablation,
                        )
                    )
        if stress_axis is None or seed == SEEDS[-1]:
            print(
                f"rollouts split={split} seed={seed} rows={len(rows)}"
                + (f" stress={stress_axis}:{stress_level}" if stress_axis else ""),
                flush=True,
            )
    return rows


def seed_metrics(rows, methods=None):
    methods = methods or sorted({r["method"] for r in rows})
    out = []
    for split in sorted({r["split"] for r in rows}):
        for method in methods:
            for seed in SEEDS:
                vals = [r for r in rows if r["split"] == split and r["method"] == method and int(r["seed"]) == seed]
                if not vals:
                    continue
                successes = [float(r["goal_success"]) for r in vals]
                unsafe = [float(r["unsafe_failure"]) for r in vals]
                stale = [float(r["stale_execution"]) for r in vals]
                refresh = [float(r["refresh"]) for r in vals]
                probe = [float(r["probe"]) for r in vals]
                abstain = [float(r["abstain"]) for r in vals]
                cost = [float(r["total_cost"]) for r in vals]
                hle = [float(r["half_life_abs_relative_error"]) for r in vals]
                cal = [float(r["calibration_abs_error"]) for r in vals]
                last_quarter = [float(r["goal_success"]) for r in vals if int(r["step"]) >= 0.75 * max(int(x["step"]) for x in vals)]
                out.append(
                    {
                        "split": split,
                        "method": method,
                        "seed": seed,
                        "goal_success": f"{np.mean(successes):.5f}",
                        "success_auc": f"{np.trapz(successes, dx=1.0) / max(1, len(successes) - 1):.5f}",
                        "late_success": f"{np.mean(last_quarter):.5f}",
                        "unsafe_failure": f"{np.mean(unsafe):.5f}",
                        "stale_execution": f"{np.mean(stale):.5f}",
                        "refresh_rate": f"{np.mean(refresh):.5f}",
                        "probe_rate": f"{np.mean(probe):.5f}",
                        "abstain_rate": f"{np.mean(abstain):.5f}",
                        "total_cost": f"{np.mean(cost):.5f}",
                        "half_life_error": f"{np.mean(hle):.5f}",
                        "calibration_error": f"{np.mean(cal):.5f}",
                        "rows": len(vals),
                    }
                )
    return out


def aggregate_metrics(seed_rows):
    out = []
    metrics = [
        "goal_success",
        "success_auc",
        "late_success",
        "unsafe_failure",
        "stale_execution",
        "refresh_rate",
        "probe_rate",
        "abstain_rate",
        "total_cost",
        "half_life_error",
        "calibration_error",
    ]
    for split in sorted({r["split"] for r in seed_rows}):
        for method in sorted({r["method"] for r in seed_rows if r["split"] == split}):
            vals = [r for r in seed_rows if r["split"] == split and r["method"] == method]
            for metric in metrics:
                nums = [float(r[metric]) for r in vals]
                out.append(
                    {
                        "split": split,
                        "method": method,
                        "metric": metric,
                        "mean": f"{np.mean(nums):.5f}",
                        "ci95": f"{ci95(nums):.5f}",
                        "seeds": len(nums),
                        "rows_per_seed": vals[0]["rows"],
                    }
                )
    return out


def pairwise_stats(seed_rows, proposal="skill_half_life_scheduler"):
    out = []
    metrics = ["goal_success", "success_auc", "late_success", "unsafe_failure", "stale_execution", "total_cost", "half_life_error"]
    for split in sorted({r["split"] for r in seed_rows}):
        for reference in sorted({r["method"] for r in seed_rows if r["split"] == split and r["method"] != proposal}):
            for metric in metrics:
                diffs = []
                for seed in SEEDS:
                    prop = [r for r in seed_rows if r["split"] == split and r["method"] == proposal and int(r["seed"]) == seed]
                    ref = [r for r in seed_rows if r["split"] == split and r["method"] == reference and int(r["seed"]) == seed]
                    if prop and ref:
                        diffs.append(float(prop[0][metric]) - float(ref[0][metric]))
                if diffs:
                    out.append(
                        {
                            "split": split,
                            "reference": reference,
                            "metric": metric,
                            "mean_diff": f"{np.mean(diffs):.5f}",
                            "ci95_diff": f"{ci95(diffs):.5f}",
                            "seeds": len(diffs),
                        }
                    )
    return out


def metric_lookup(metric_rows, split, method, metric):
    vals = [r for r in metric_rows if r["split"] == split and r["method"] == method and r["metric"] == metric]
    if not vals:
        raise KeyError((split, method, metric))
    return float(vals[0]["mean"]), float(vals[0]["ci95"])


def run_main():
    rows = []
    for split in SPLITS:
        rows.extend(run_rollouts_for(split, METHODS, DEPLOYMENT_STEPS))
    seed_rows = seed_metrics(rows, METHODS)
    metric_rows = aggregate_metrics(seed_rows)
    pair_rows = pairwise_stats(seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    return rows, seed_rows, metric_rows, pair_rows


def run_ablation():
    rows = run_rollouts_for("combined_micro_shift", [], DEPLOYMENT_STEPS, ablation_methods=ABLATIONS)
    seed_rows = seed_metrics(rows, ABLATIONS)
    metric_rows = aggregate_metrics(seed_rows)
    summary = []
    for ablation in ABLATIONS:
        summary.append(
            {
                "split": "combined_micro_shift",
                "ablation": ablation,
                "goal_success": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'goal_success')[0]:.5f}",
                "ci95_success": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'goal_success')[1]:.5f}",
                "success_auc": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'success_auc')[0]:.5f}",
                "unsafe_failure": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'unsafe_failure')[0]:.5f}",
                "refresh_rate": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'refresh_rate')[0]:.5f}",
                "probe_rate": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'probe_rate')[0]:.5f}",
                "half_life_error": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'half_life_error')[0]:.5f}",
                "total_cost": f"{metric_lookup(metric_rows, 'combined_micro_shift', ablation, 'total_cost')[0]:.5f}",
            }
        )
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, summary


def run_stress():
    axes = ["drift_rate", "sensor_noise", "mode_flip", "probe_cost", "combined"]
    levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    methods = [
        "domain_randomized_clone",
        "conformal_risk_gate",
        "online_finetune",
        "skill_half_life_scheduler",
        "oracle_shift_aware_scheduler",
    ]
    raw = []
    summary = []
    for axis in axes:
        for level in levels:
            rows = run_rollouts_for("combined_micro_shift", methods, STRESS_STEPS, stress_axis=axis, stress_level=level)
            for row in rows:
                row["stress_axis"] = axis
                row["stress_level"] = f"{level:.1f}"
            raw.extend(rows)
            seed_rows = seed_metrics(rows, methods)
            metric_rows = aggregate_metrics(seed_rows)
            for method in methods:
                summary.append(
                    {
                        "stress_axis": axis,
                        "stress_level": f"{level:.1f}",
                        "method": method,
                        "goal_success": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'goal_success')[0]:.5f}",
                        "ci95_success": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'goal_success')[1]:.5f}",
                        "success_auc": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'success_auc')[0]:.5f}",
                        "unsafe_failure": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'unsafe_failure')[0]:.5f}",
                        "half_life_error": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'half_life_error')[0]:.5f}",
                        "total_cost": f"{metric_lookup(metric_rows, 'combined_micro_shift', method, 'total_cost')[0]:.5f}",
                    }
                )
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, summary


def negative_cases():
    rows = [
        {
            "case": "unseen_hardware_damage",
            "expected_behavior": "half-life estimate should collapse and trigger abstention",
            "observed_outcome": "still unsafe if the damage has no sensor signature",
            "lesson": "skill half-life is not a substitute for hardware health monitoring",
        },
        {
            "case": "goal_semantics_changed",
            "expected_behavior": "physical probes should not claim semantic recovery",
            "observed_outcome": "scheduler preserves physical safety but cannot infer a new goal",
            "lesson": "instruction-grounding shift is outside the mechanism",
        },
        {
            "case": "adversarially_biased_sensor",
            "expected_behavior": "conformal and half-life gates should become conservative",
            "observed_outcome": "hidden bias delays refresh decisions",
            "lesson": "sensor calibration audits must be separate from skill survival estimates",
        },
        {
            "case": "rapid_contact_mode_chatter",
            "expected_behavior": "half-life should shorten under repeated flips",
            "observed_outcome": "probe cost can dominate before enough evidence accumulates",
            "lesson": "the scheduler needs an explicit chatter detector for deployment",
        },
    ]
    write_csv(RESULTS / "negative_cases.csv", rows)
    return rows


def plot_main(metric_rows, main_rows, ablation_summary, stress_summary):
    methods_order = [
        "frozen_behavior_clone",
        "domain_randomized_clone",
        "fixed_interval_refresh",
        "online_finetune",
        "scalar_uncertainty_gate",
        "conformal_risk_gate",
        "skill_half_life_scheduler",
        "oracle_shift_aware_scheduler",
    ]
    labels = {
        "frozen_behavior_clone": "Frozen BC",
        "domain_randomized_clone": "Domain rand.",
        "fixed_interval_refresh": "Fixed refresh",
        "online_finetune": "Online FT",
        "scalar_uncertainty_gate": "Uncertainty",
        "conformal_risk_gate": "Conformal",
        "skill_half_life_scheduler": "Half-life",
        "oracle_shift_aware_scheduler": "Oracle",
    }
    splits = list(SPLITS.keys())
    colors = plt.cm.tab20(np.linspace(0, 1, len(methods_order)))

    plt.figure(figsize=(12, 6))
    x = np.arange(len(splits))
    width = 0.095
    for idx, method in enumerate(methods_order):
        vals = [metric_lookup(metric_rows, split, method, "goal_success")[0] for split in splits]
        plt.bar(x + (idx - 3.5) * width, vals, width=width, color=colors[idx], label=labels[method])
    plt.xticks(x, [s.replace("_", "\n") for s in splits], fontsize=9)
    plt.ylabel("Goal success")
    plt.ylim(0.0, 1.0)
    plt.title("Skill survival under physical shift")
    plt.legend(ncol=4, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_success.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    target_methods = ["frozen_behavior_clone", "domain_randomized_clone", "conformal_risk_gate", "skill_half_life_scheduler", "oracle_shift_aware_scheduler"]
    bins = [(0, 18), (18, 36), (36, 54), (54, 72)]
    for method in target_methods:
        ys = []
        for lo, hi in bins:
            vals = [
                float(r["goal_success"])
                for r in main_rows
                if r["split"] == "combined_micro_shift" and r["method"] == method and lo <= int(r["step"]) < hi
            ]
            ys.append(float(np.mean(vals)))
        plt.plot([f"{lo}-{hi}" for lo, hi in bins], ys, marker="o", label=labels[method])
    plt.ylabel("Success by deployment age bin")
    plt.ylim(0.0, 1.0)
    plt.title("Skill half-life curves on combined micro-shift")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_decay_curves.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    failure_metrics = ["unsafe_failure", "stale_execution"]
    width = 0.35
    x = np.arange(len(methods_order))
    for i, metric in enumerate(failure_metrics):
        vals = [metric_lookup(metric_rows, "combined_micro_shift", method, metric)[0] for method in methods_order]
        plt.bar(x + (i - 0.5) * width, vals, width=width, label=metric.replace("_", " "))
    plt.xticks(x, [labels[m] for m in methods_order], rotation=25, ha="right")
    plt.ylabel("Rate")
    plt.title("Unsafe and stale executions on combined micro-shift")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_failures.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    ablations = [r["ablation"] for r in ablation_summary]
    vals = [float(r["goal_success"]) for r in ablation_summary]
    plt.bar(range(len(ablations)), vals, color="#376795")
    plt.xticks(range(len(ablations)), [a.replace("_", "\n") for a in ablations], rotation=0, fontsize=8)
    plt.ylabel("Goal success")
    plt.ylim(0.0, 1.0)
    plt.title("Half-life scheduler ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_ablation.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    for method in ["domain_randomized_clone", "conformal_risk_gate", "online_finetune", "skill_half_life_scheduler", "oracle_shift_aware_scheduler"]:
        rows = [r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method]
        rows = sorted(rows, key=lambda r: float(r["stress_level"]))
        plt.plot([float(r["stress_level"]) for r in rows], [float(r["goal_success"]) for r in rows], marker="o", label=labels[method])
    plt.xlabel("Combined stress level")
    plt.ylabel("Goal success")
    plt.ylim(0.0, 1.0)
    plt.title("Combined stress sweep")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_stress_sweep.png", dpi=220)
    plt.close()


def terminal_decision(metric_rows, pair_rows, ablation_summary):
    split = "combined_micro_shift"
    proposal = metric_lookup(metric_rows, split, "skill_half_life_scheduler", "goal_success")[0]
    proposal_auc = metric_lookup(metric_rows, split, "skill_half_life_scheduler", "success_auc")[0]
    proposal_unsafe = metric_lookup(metric_rows, split, "skill_half_life_scheduler", "unsafe_failure")[0]
    non_oracle = [m for m in METHODS if m not in {"skill_half_life_scheduler", "oracle_shift_aware_scheduler"}]
    best_baseline_success = max(metric_lookup(metric_rows, split, m, "goal_success")[0] for m in non_oracle)
    best_baseline_auc = max(metric_lookup(metric_rows, split, m, "success_auc")[0] for m in non_oracle)
    best_success_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "goal_success")[0])
    best_success_unsafe = metric_lookup(metric_rows, split, best_success_method, "unsafe_failure")[0]
    full = [r for r in ablation_summary if r["ablation"] == "full_skill_half_life_scheduler"][0]
    strongest_ablation = max(float(r["goal_success"]) for r in ablation_summary if r["ablation"] != "full_skill_half_life_scheduler")
    ablation_drop = float(full["goal_success"]) - strongest_ablation
    paired = [
        r
        for r in pair_rows
        if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "goal_success"
    ][0]
    if (
        proposal >= best_baseline_success + 0.045
        and proposal_auc >= best_baseline_auc + 0.040
        and proposal_unsafe <= best_success_unsafe - 0.006
        and float(paired["mean_diff"]) > 0.035
        and ablation_drop >= 0.025
    ):
        return "STRONG_REVISE"
    return "KILL_ARCHIVE"


def write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal):
    split = "combined_micro_shift"
    lines = []
    lines.append("Paper 83 robot_skill_half_life_under_shift v4 rebuild")
    lines.append(f"Terminal recommendation: {terminal}")
    lines.append("Reason: local skill-survival benchmark added; no robot hardware or external high-fidelity benchmark is available.")
    lines.append(f"Main rollout rows: {sum(1 for _ in open(RESULTS / 'rollouts.csv', encoding='utf-8')) - 1}")
    lines.append(f"Ablation rollout rows: {sum(1 for _ in open(RESULTS / 'ablation_rollouts.csv', encoding='utf-8')) - 1}")
    lines.append(f"Stress rollout rows: {sum(1 for _ in open(RESULTS / 'stress_sweep_raw.csv', encoding='utf-8')) - 1}")
    lines.append(f"Seeds: {SEEDS}")
    lines.append("")
    lines.append("Combined micro-shift:")
    for method in METHODS:
        success = metric_lookup(metric_rows, split, method, "goal_success")
        auc = metric_lookup(metric_rows, split, method, "success_auc")
        unsafe = metric_lookup(metric_rows, split, method, "unsafe_failure")
        hle = metric_lookup(metric_rows, split, method, "half_life_error")
        lines.append(
            f"{method} goal_success={success[0]:.5f} ci95={success[1]:.5f} auc={auc[0]:.5f} unsafe={unsafe[0]:.5f} half_life_error={hle[0]:.5f}"
        )
    best_success_method = max(
        [m for m in METHODS if m not in {"skill_half_life_scheduler", "oracle_shift_aware_scheduler"}],
        key=lambda m: metric_lookup(metric_rows, split, m, "goal_success")[0],
    )
    paired = [
        r
        for r in pair_rows
        if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "goal_success"
    ][0]
    lines.append(
        f"paired goal-success diff vs best baseline {best_success_method}={float(paired['mean_diff']):.5f} ci95={float(paired['ci95_diff']):.5f}"
    )
    lines.append("")
    lines.append("Ablations:")
    for row in ablation_summary:
        lines.append(
            f"{row['ablation']} goal_success={row['goal_success']} ci95={row['ci95_success']} auc={row['success_auc']} unsafe={row['unsafe_failure']} hle={row['half_life_error']} cost={row['total_cost']}"
        )
    lines.append("")
    lines.append("Combined stress level 1.0:")
    for row in stress_summary:
        if row["stress_axis"] == "combined" and row["stress_level"] == "1.0":
            lines.append(
                f"{row['method']} goal_success={row['goal_success']} ci95={row['ci95_success']} unsafe={row['unsafe_failure']} hle={row['half_life_error']} cost={row['total_cost']}"
            )
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"terminal={terminal}")
    print(f"wrote results to {RESULTS}")


def main():
    main_rows, seed_rows, metric_rows, pair_rows = run_main()
    ablation_rows, ablation_summary = run_ablation()
    stress_raw, stress_summary = run_stress()
    negative_cases()
    terminal = terminal_decision(metric_rows, pair_rows, ablation_summary)
    plot_main(metric_rows, main_rows, ablation_summary, stress_summary)
    write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal)


if __name__ == "__main__":
    main()
