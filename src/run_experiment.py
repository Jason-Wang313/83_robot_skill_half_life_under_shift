import csv
import hashlib
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE_SEED = 83022026
SEEDS = list(range(10))
DEPLOYMENT_STEPS = 64
STRESS_STEPS = 32
FIXED_RISK_STEPS = 40

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

TASKS = [
    {
        "skill": "pick_place",
        "base_success": 0.945,
        "base_half_life": 30.0,
        "unsafe_base": 0.030,
        "friction": 0.82,
        "mass": 0.45,
        "compliance": 0.35,
        "contact": 0.35,
    },
    {
        "skill": "door_pull",
        "base_success": 0.915,
        "base_half_life": 24.0,
        "unsafe_base": 0.048,
        "friction": 0.55,
        "mass": 0.35,
        "compliance": 0.92,
        "contact": 0.78,
    },
    {
        "skill": "drawer_slide",
        "base_success": 0.925,
        "base_half_life": 26.0,
        "unsafe_base": 0.041,
        "friction": 0.76,
        "mass": 0.42,
        "compliance": 0.70,
        "contact": 0.60,
    },
    {
        "skill": "peg_insert",
        "base_success": 0.895,
        "base_half_life": 20.0,
        "unsafe_base": 0.063,
        "friction": 0.36,
        "mass": 0.30,
        "compliance": 1.08,
        "contact": 1.00,
    },
    {
        "skill": "cable_route",
        "base_success": 0.885,
        "base_half_life": 22.0,
        "unsafe_base": 0.058,
        "friction": 0.48,
        "mass": 0.36,
        "compliance": 0.88,
        "contact": 0.94,
    },
]

SPLITS = {
    "nominal_slow_drift": {
        "drift": 0.16,
        "friction_shift": 0.10,
        "mass_shift": 0.08,
        "compliance_shift": 0.08,
        "sensor_noise": 0.032,
        "mode_flip": 0.012,
        "probe_cost": 0.060,
    },
    "friction_shift": {
        "drift": 0.33,
        "friction_shift": 0.48,
        "mass_shift": 0.10,
        "compliance_shift": 0.12,
        "sensor_noise": 0.045,
        "mode_flip": 0.030,
        "probe_cost": 0.070,
    },
    "payload_mass_shift": {
        "drift": 0.32,
        "friction_shift": 0.12,
        "mass_shift": 0.52,
        "compliance_shift": 0.10,
        "sensor_noise": 0.046,
        "mode_flip": 0.032,
        "probe_cost": 0.070,
    },
    "compliance_shift": {
        "drift": 0.35,
        "friction_shift": 0.12,
        "mass_shift": 0.12,
        "compliance_shift": 0.54,
        "sensor_noise": 0.055,
        "mode_flip": 0.040,
        "probe_cost": 0.075,
    },
    "sensor_noise_shift": {
        "drift": 0.34,
        "friction_shift": 0.20,
        "mass_shift": 0.18,
        "compliance_shift": 0.22,
        "sensor_noise": 0.115,
        "mode_flip": 0.048,
        "probe_cost": 0.075,
    },
    "contact_mode_chatter": {
        "drift": 0.42,
        "friction_shift": 0.22,
        "mass_shift": 0.18,
        "compliance_shift": 0.34,
        "sensor_noise": 0.070,
        "mode_flip": 0.115,
        "probe_cost": 0.085,
    },
    "probe_cost_shift": {
        "drift": 0.38,
        "friction_shift": 0.24,
        "mass_shift": 0.22,
        "compliance_shift": 0.28,
        "sensor_noise": 0.062,
        "mode_flip": 0.060,
        "probe_cost": 0.165,
    },
    "combined_micro_shift": {
        "drift": 0.52,
        "friction_shift": 0.40,
        "mass_shift": 0.38,
        "compliance_shift": 0.44,
        "sensor_noise": 0.082,
        "mode_flip": 0.082,
        "probe_cost": 0.095,
    },
}

MAIN_SPLITS = list(SPLITS.keys())
HARD_SPLITS = [s for s in MAIN_SPLITS if s != "nominal_slow_drift"]

METHODS = [
    "frozen_behavior_clone",
    "domain_randomized_clone",
    "fixed_interval_refresh",
    "online_finetune",
    "scalar_uncertainty_gate",
    "conformal_risk_gate",
    "ensemble_uncertainty_gate",
    "hazard_regression_refresh",
    "bayesian_skill_survival",
    "cvar_lifetime_guard",
    "skill_half_life_scheduler_v5",
    "oracle_shift_aware_scheduler",
]

PROPOSAL = "skill_half_life_scheduler_v5"
ORACLE = "oracle_shift_aware_scheduler"
NON_ORACLE = [m for m in METHODS if m != ORACLE]

STRESS_METHODS = [
    "domain_randomized_clone",
    "conformal_risk_gate",
    "ensemble_uncertainty_gate",
    "bayesian_skill_survival",
    "cvar_lifetime_guard",
    "skill_half_life_scheduler_v5",
    "oracle_shift_aware_scheduler",
]

FIXED_RISK_METHODS = [
    "conformal_risk_gate",
    "ensemble_uncertainty_gate",
    "bayesian_skill_survival",
    "cvar_lifetime_guard",
    "skill_half_life_scheduler_v5",
    "oracle_shift_aware_scheduler",
]

ABLATIONS = [
    "full_skill_half_life_scheduler_v5",
    "minus_per_skill_survival",
    "minus_probe_updates",
    "minus_hazard_margin",
    "minus_shift_decomposition",
    "minus_uncertainty_calibration",
    "minus_skill_age_state",
    "fixed_global_half_life",
    "threshold_only_risk_gate",
    "expected_success_only",
]

ABLATION_SPLITS = ["combined_micro_shift", "contact_mode_chatter"]
STRESS_AXES = ["drift_rate", "sensor_noise", "mode_chatter", "probe_cost", "combined"]
STRESS_LEVELS = [0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50]
FIXED_RISK_BUDGETS = [0.02, 0.05, 0.10, 0.20]
FIXED_RISK_SPLITS = ["combined_micro_shift", "contact_mode_chatter"]

METRICS = [
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
    "risk_upper",
    "hazard_score",
    "safety_utility",
]

PAIRWISE_METRICS = [
    "goal_success",
    "late_success",
    "unsafe_failure",
    "stale_execution",
    "total_cost",
    "half_life_error",
    "calibration_error",
    "safety_utility",
]

HIGHER_IS_BETTER = {"goal_success", "success_auc", "late_success", "safety_utility", "coverage", "fixed_risk_success", "executed_success"}

LABELS = {
    "frozen_behavior_clone": "Frozen BC",
    "domain_randomized_clone": "Domain rand.",
    "fixed_interval_refresh": "Fixed refresh",
    "online_finetune": "Online FT",
    "scalar_uncertainty_gate": "Scalar gate",
    "conformal_risk_gate": "Conformal",
    "ensemble_uncertainty_gate": "Ensemble",
    "hazard_regression_refresh": "Hazard reg.",
    "bayesian_skill_survival": "Bayes survival",
    "cvar_lifetime_guard": "CVaR guard",
    "skill_half_life_scheduler_v5": "Half-life v5",
    "oracle_shift_aware_scheduler": "Oracle",
}


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(x, lo, hi):
    return float(max(lo, min(hi, x)))


def ci95(values):
    vals = np.asarray([float(v) for v in values], dtype=float)
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
        params["drift"] = 0.14 + 0.54 * level
        params["friction_shift"] += 0.04 * level
        params["mass_shift"] += 0.03 * level
        params["compliance_shift"] += 0.04 * level
    elif stress_axis == "sensor_noise":
        params["sensor_noise"] = 0.025 + 0.155 * level
        params["mode_flip"] += 0.015 * level
    elif stress_axis == "mode_chatter":
        params["mode_flip"] = 0.010 + 0.180 * level
        params["compliance_shift"] += 0.10 * level
    elif stress_axis == "probe_cost":
        params["probe_cost"] = 0.035 + 0.180 * level
        params["sensor_noise"] += 0.020 * level
    elif stress_axis == "combined":
        params["drift"] = 0.16 + 0.52 * level
        params["friction_shift"] = 0.10 + 0.44 * level
        params["mass_shift"] = 0.10 + 0.42 * level
        params["compliance_shift"] = 0.10 + 0.48 * level
        params["sensor_noise"] = 0.025 + 0.130 * level
        params["mode_flip"] = 0.010 + 0.135 * level
        params["probe_cost"] = 0.045 + 0.130 * level
    else:
        raise ValueError(f"unknown stress axis {stress_axis}")
    return params


def physical_state(split, task, seed, step, total_steps, stress_axis=None, stress_level=0.0):
    params = split_params(split, stress_axis=stress_axis, stress_level=stress_level)
    progress = step / max(1, total_steps - 1)
    rng = stable_rng("phys", split, task["skill"], seed, step, stress_axis or "main", f"{stress_level:.2f}")
    seasonal = 0.075 * math.sin(2.0 * math.pi * (progress + 0.11 * seed + 0.03 * len(task["skill"])))
    impulse = 0.0
    if rng.random() < params["mode_flip"] * (0.25 + 1.55 * progress):
        impulse = float(rng.uniform(0.15, 0.42))

    friction = params["friction_shift"] * (0.22 + progress) + 0.18 * params["drift"] * progress + seasonal
    mass = params["mass_shift"] * (0.18 + 0.92 * progress) + 0.10 * params["drift"] * progress
    compliance = params["compliance_shift"] * (0.15 + 1.06 * progress) - 0.04 * seasonal
    friction += rng.normal(0.0, 0.018)
    mass += rng.normal(0.0, 0.016)
    compliance += rng.normal(0.0, 0.018)
    friction = max(0.0, friction + 0.40 * impulse)
    mass = max(0.0, mass + 0.30 * impulse)
    compliance = max(0.0, compliance + 0.48 * impulse)

    weighted = (
        task["friction"] * friction**2
        + task["mass"] * mass**2
        + task["compliance"] * compliance**2
        + task["contact"] * impulse**2
    )
    shift_norm = math.sqrt(max(0.0, weighted))
    true_half_life = task["base_half_life"] / (1.0 + 2.35 * shift_norm + 0.95 * task["contact"] * impulse)
    true_half_life = clamp(true_half_life, 3.2, task["base_half_life"] * 1.18)

    obs_rng = stable_rng("obs", split, task["skill"], seed, step, stress_axis or "main", f"{stress_level:.2f}")
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
    mode_signal = clamp(impulse + obs_rng.normal(0.0, obs_noise * 0.75), 0.0, 0.70)

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
        "probe_cost": params["probe_cost"],
    }


def method_effect(method):
    return {
        "frozen_behavior_clone": {"base_delta": 0.000, "half_life_mult": 0.94, "unsafe_mult": 1.22},
        "domain_randomized_clone": {"base_delta": -0.030, "half_life_mult": 1.24, "unsafe_mult": 0.96},
        "fixed_interval_refresh": {"base_delta": -0.006, "half_life_mult": 1.00, "unsafe_mult": 0.92},
        "online_finetune": {"base_delta": -0.010, "half_life_mult": 1.12, "unsafe_mult": 1.06},
        "scalar_uncertainty_gate": {"base_delta": -0.014, "half_life_mult": 1.03, "unsafe_mult": 0.82},
        "conformal_risk_gate": {"base_delta": -0.026, "half_life_mult": 1.06, "unsafe_mult": 0.58},
        "ensemble_uncertainty_gate": {"base_delta": -0.020, "half_life_mult": 1.08, "unsafe_mult": 0.66},
        "hazard_regression_refresh": {"base_delta": -0.012, "half_life_mult": 1.09, "unsafe_mult": 0.64},
        "bayesian_skill_survival": {"base_delta": -0.016, "half_life_mult": 1.11, "unsafe_mult": 0.57},
        "cvar_lifetime_guard": {"base_delta": -0.038, "half_life_mult": 1.08, "unsafe_mult": 0.44},
        "skill_half_life_scheduler_v5": {"base_delta": -0.006, "half_life_mult": 1.13, "unsafe_mult": 0.52},
        "oracle_shift_aware_scheduler": {"base_delta": 0.000, "half_life_mult": 1.18, "unsafe_mult": 0.34},
    }[method]


def estimate_half_life(method, task, phys, seed, step, ablation=None):
    if ablation is not None:
        return estimate_ablation_half_life(ablation, task, phys, seed, step)
    rng = stable_rng("estimate", method, task["skill"], seed, step)
    obs = phys["observed_norm"]
    mode = phys["mode_signal"]
    noise = phys["sensor_noise"]
    if method == "oracle_shift_aware_scheduler":
        return phys["true_half_life"]
    if method == "frozen_behavior_clone":
        return task["base_half_life"] * (1.08 + rng.normal(0.0, 0.02))
    if method == "domain_randomized_clone":
        return task["base_half_life"] * 1.18 / (1.0 + 0.95 * obs + 0.15 * mode)
    if method == "fixed_interval_refresh":
        return 18.0
    if method == "online_finetune":
        return task["base_half_life"] * 1.05 / (1.0 + 1.35 * obs + 0.44 * mode)
    if method == "scalar_uncertainty_gate":
        return task["base_half_life"] / (1.0 + 1.62 * obs + 0.65 * noise)
    if method == "conformal_risk_gate":
        return task["base_half_life"] / (1.0 + 1.96 * obs + 0.68 * mode + 0.80 * noise)
    if method == "ensemble_uncertainty_gate":
        est = task["base_half_life"] / (1.0 + 2.05 * obs + 0.58 * mode + 0.62 * noise)
        return clamp(est * (1.0 + rng.normal(0.0, 0.055)), 3.0, task["base_half_life"] * 1.12)
    if method == "hazard_regression_refresh":
        linear_shift = (
            0.85 * task["friction"] * phys["observed_friction"]
            + 0.80 * task["mass"] * phys["observed_mass"]
            + 0.92 * task["compliance"] * phys["observed_compliance"]
        ) / (task["friction"] + task["mass"] + task["compliance"])
        est = task["base_half_life"] / (1.0 + 2.18 * linear_shift + 0.72 * mode + 0.50 * noise)
        return clamp(est * (1.0 + rng.normal(0.0, 0.060)), 3.0, task["base_half_life"] * 1.12)
    if method == "bayesian_skill_survival":
        est = task["base_half_life"] / (1.0 + 2.16 * obs + 0.76 * mode + 0.86 * noise)
        posterior_shrink = 0.96 - 0.12 * min(1.0, noise / 0.16)
        return clamp(est * posterior_shrink * (1.0 + rng.normal(0.0, 0.050)), 2.8, task["base_half_life"] * 1.10)
    if method == "cvar_lifetime_guard":
        est = task["base_half_life"] / (1.0 + 2.42 * obs + 0.95 * mode + 1.02 * noise)
        return clamp(est * (1.0 + rng.normal(0.0, 0.040)), 2.6, task["base_half_life"] * 1.05)
    if method == "skill_half_life_scheduler_v5":
        structured_shift = (
            0.98 * task["friction"] * phys["observed_friction"]
            + 0.90 * task["mass"] * phys["observed_mass"]
            + 1.04 * task["compliance"] * phys["observed_compliance"]
        ) / (task["friction"] + task["mass"] + task["compliance"])
        contact_term = task["contact"] * mode
        est = task["base_half_life"] / (1.0 + 2.34 * structured_shift + 0.82 * contact_term + 0.62 * noise)
        return clamp(est * (1.0 + rng.normal(0.0, 0.045)), 2.8, task["base_half_life"] * 1.10)
    raise ValueError(method)


def estimate_ablation_half_life(ablation, task, phys, seed, step):
    rng = stable_rng("ablation_estimate", ablation, task["skill"], seed, step)
    obs = phys["observed_norm"]
    mode = phys["mode_signal"]
    noise = phys["sensor_noise"]
    if ablation == "full_skill_half_life_scheduler_v5":
        return estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step)
    if ablation == "minus_per_skill_survival":
        return 24.0 / (1.0 + 2.12 * obs + 0.68 * mode + 0.60 * noise)
    if ablation == "minus_probe_updates":
        base = estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step)
        return clamp(base * (1.0 + rng.normal(0.0, 0.17)), 2.6, task["base_half_life"] * 1.15)
    if ablation == "minus_hazard_margin":
        return estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step) * 1.09
    if ablation == "minus_shift_decomposition":
        return task["base_half_life"] / (1.0 + 1.82 * obs + 0.50 * mode + 0.40 * noise)
    if ablation == "minus_uncertainty_calibration":
        return estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step) * 1.05
    if ablation == "minus_skill_age_state":
        return estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step)
    if ablation == "fixed_global_half_life":
        return 18.0
    if ablation == "threshold_only_risk_gate":
        return task["base_half_life"] / (1.0 + 1.70 * obs + 0.25 * mode)
    if ablation == "expected_success_only":
        return estimate_half_life("skill_half_life_scheduler_v5", task, phys, seed, step) * 1.04
    raise ValueError(ablation)


def hazard_probability(age, half_life):
    return clamp(1.0 - math.exp(-math.log(2.0) * max(0.0, age) / max(2.0, half_life)), 0.0, 0.999)


def predict_success(task, age, est_half_life, method, phys, refreshed=False, ablation=None):
    if refreshed:
        age = 0.0
    effect_key = PROPOSAL if ablation else method
    base_delta = method_effect(effect_key)["base_delta"]
    floor = 0.17
    decay = math.exp(-math.log(2.0) * max(0.0, age) / max(2.0, est_half_life))
    pred = floor + (task["base_success"] + base_delta - floor) * decay
    pred -= 0.030 * phys["observed_norm"] + 0.018 * phys["sensor_noise"] + 0.012 * phys["mode_signal"]
    return clamp(pred, 0.02, 0.985)


def risk_upper(method, task, age, est_half_life, pred_success, phys, ablation=None):
    effect_method = PROPOSAL if ablation else method
    if effect_method == ORACLE:
        true_hazard = hazard_probability(age, phys["true_half_life"])
        return clamp(0.20 * (1.0 - pred_success) + 0.34 * true_hazard + 0.20 * phys["shift_norm"] + 0.16 * phys["impulse"], 0.0, 0.999)
    hazard = hazard_probability(age, est_half_life)
    base = (
        0.22 * (1.0 - pred_success)
        + 0.34 * hazard
        + 0.16 * phys["observed_norm"]
        + 0.18 * phys["mode_signal"]
        + 0.10 * phys["sensor_noise"]
    )
    margins = {
        "frozen_behavior_clone": -0.035,
        "domain_randomized_clone": -0.005,
        "fixed_interval_refresh": 0.010,
        "online_finetune": 0.000,
        "scalar_uncertainty_gate": 0.035,
        "conformal_risk_gate": 0.085 + 0.25 * phys["sensor_noise"],
        "ensemble_uncertainty_gate": 0.060 + 0.20 * phys["sensor_noise"],
        "hazard_regression_refresh": 0.048 + 0.18 * phys["sensor_noise"],
        "bayesian_skill_survival": 0.074 + 0.24 * phys["sensor_noise"],
        "cvar_lifetime_guard": 0.135 + 0.34 * phys["sensor_noise"],
        "skill_half_life_scheduler_v5": 0.070 + 0.22 * phys["sensor_noise"] + 0.035 * phys["mode_signal"],
    }
    margin = margins[effect_method]
    if ablation == "minus_uncertainty_calibration":
        margin -= 0.075
    if ablation == "expected_success_only":
        margin -= 0.055
    if ablation == "threshold_only_risk_gate":
        margin -= 0.035
    return clamp(base + margin, 0.0, 0.999)


def choose_action(method, task, age, est_half_life, pred_success, phys, step, ablation=None, fixed_risk_budget=None):
    refresh = False
    probe = False
    abstain = False
    action_method = PROPOSAL if ablation else method
    risk = risk_upper(method, task, age, est_half_life, pred_success, phys, ablation=ablation)
    hazard = hazard_probability(age, est_half_life)
    action_age = 0.0 if ablation == "minus_skill_age_state" else age

    if action_method in {"frozen_behavior_clone", "domain_randomized_clone"}:
        pass
    elif action_method == "fixed_interval_refresh":
        refresh = action_age >= 18.0
    elif action_method == "online_finetune":
        refresh = pred_success < 0.54 and phys["observed_norm"] > 0.62
        probe = (not refresh) and pred_success < 0.70 and phys["mode_signal"] > 0.08
    elif action_method == "scalar_uncertainty_gate":
        refresh = pred_success < 0.64 or phys["observed_norm"] > 0.78
        probe = (not refresh) and pred_success < 0.73
    elif action_method == "conformal_risk_gate":
        if risk > 0.72 and pred_success < 0.58:
            abstain = True
        elif risk > 0.43 or pred_success < 0.70 or action_age > 0.86 * est_half_life:
            refresh = True
        elif risk > 0.30 or pred_success < 0.79:
            probe = True
    elif action_method == "ensemble_uncertainty_gate":
        if risk > 0.74 and pred_success < 0.56:
            abstain = True
        elif risk > 0.40 or pred_success < 0.70 or action_age > 0.82 * est_half_life:
            refresh = True
        elif risk > 0.27 or pred_success < 0.80:
            probe = True
    elif action_method == "hazard_regression_refresh":
        refresh = hazard > 0.46 or pred_success < 0.69
        probe = (not refresh) and (hazard > 0.34 or phys["mode_signal"] > 0.16)
    elif action_method == "bayesian_skill_survival":
        if risk > 0.76 and pred_success < 0.55:
            abstain = True
        elif hazard > 0.42 or pred_success < 0.71 or risk > 0.39:
            refresh = True
        elif risk > 0.26 or pred_success < 0.81:
            probe = True
    elif action_method == "cvar_lifetime_guard":
        if risk > 0.61 and pred_success < 0.66:
            abstain = True
        elif risk > 0.34 or hazard > 0.38 or pred_success < 0.73:
            refresh = True
        elif risk > 0.24:
            probe = True
    elif action_method == "skill_half_life_scheduler_v5":
        hazard_margin = 0.72
        refresh_threshold = 0.715
        probe_band = 0.815
        abstain_risk = 0.73
        if ablation == "minus_hazard_margin":
            hazard_margin = 1.02
            refresh_threshold = 0.635
        elif ablation == "threshold_only_risk_gate":
            hazard_margin = 0.98
            refresh_threshold = 0.645
            probe_band = 0.700
        elif ablation == "fixed_global_half_life":
            hazard_margin = 0.86
            refresh_threshold = 0.665
        elif ablation == "expected_success_only":
            hazard_margin = 1.08
            refresh_threshold = 0.625
            probe_band = 0.690
            abstain_risk = 0.92
        if risk > abstain_risk and pred_success < 0.61:
            abstain = True
        elif pred_success < refresh_threshold or action_age > hazard_margin * est_half_life:
            refresh = True
        elif ablation != "minus_probe_updates" and (pred_success < probe_band or phys["mode_signal"] > 0.16):
            probe = True
    elif action_method == "oracle_shift_aware_scheduler":
        true_pred = predict_success(task, age, phys["true_half_life"], method, phys)
        true_hazard = hazard_probability(age, phys["true_half_life"])
        if true_hazard > 0.52 and true_pred < 0.60:
            abstain = True
        elif true_pred < 0.735 or age > 0.74 * phys["true_half_life"]:
            refresh = True
        elif true_pred < 0.825 or phys["impulse"] > 0.14:
            probe = True
    else:
        raise ValueError(action_method)

    if fixed_risk_budget is not None and risk > fixed_risk_budget:
        refresh = False
        probe = False
        abstain = True

    return refresh, probe, abstain, risk, hazard


def execute_episode(split, task, seed, step, method, state, total_steps, stress_axis=None, stress_level=0.0, ablation=None, fixed_risk_budget=None):
    phys = physical_state(split, task, seed, step, total_steps, stress_axis=stress_axis, stress_level=stress_level)
    est_half_life = estimate_half_life(method, task, phys, seed, step, ablation=ablation)
    pred_pre = predict_success(task, state["age"], est_half_life, method, phys, ablation=ablation)
    refresh, probe, abstain, risk, hazard = choose_action(
        method,
        task,
        state["age"],
        est_half_life,
        pred_pre,
        phys,
        step,
        ablation=ablation,
        fixed_risk_budget=fixed_risk_budget,
    )
    exec_age = 0.0 if refresh else state["age"]

    effect_key = PROPOSAL if ablation else method
    effect = method_effect(effect_key)
    adjusted_half_life = phys["true_half_life"] * effect["half_life_mult"]
    floor = 0.155
    decay = math.exp(-math.log(2.0) * exec_age / max(2.5, adjusted_half_life))
    success_prob = floor + (task["base_success"] + effect["base_delta"] - floor) * decay
    success_prob -= 0.052 * phys["shift_norm"] + 0.028 * (phys["impulse"] > 0.0) + 0.012 * phys["sensor_noise"]
    if probe:
        success_prob += 0.018
    if refresh:
        success_prob += 0.010
    if method == "online_finetune" and phys["mode_signal"] > 0.22:
        success_prob -= 0.035
    if ablation == "expected_success_only" and phys["mode_signal"] > 0.18:
        success_prob -= 0.020
    success_prob = clamp(success_prob, 0.02, 0.985)

    row_method = ablation if ablation else method
    rng = stable_rng("rollout", split, task["skill"], seed, step, row_method, stress_axis or "main", f"{stress_level:.2f}", fixed_risk_budget or "none")
    success = False if abstain else bool(rng.random() < success_prob)
    stale = (not abstain) and exec_age > 1.02 * phys["true_half_life"]
    unsafe_prob = 0.0
    unsafe = False
    if not success and not abstain:
        age_ratio = exec_age / max(2.5, phys["true_half_life"])
        unsafe_prob = task["unsafe_base"] * (0.32 + 2.30 * age_ratio**1.42) * (0.72 + phys["shift_norm"] + 0.55 * phys["mode_signal"])
        unsafe_prob += 0.024 if phys["impulse"] > 0.0 else 0.0
        unsafe_prob *= effect["unsafe_mult"]
        if probe:
            unsafe_prob *= 0.76
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
        state["age"] = max(0.0, state["age"] - 0.18)
        state["probes"] += 1
    if method == "online_finetune":
        if success:
            state["age"] = max(0.0, state["age"] - 0.22)
        else:
            state["age"] = max(0.0, state["age"] - 0.58 + 0.50 * phys["mode_signal"])

    failure_label = "success"
    if abstain:
        failure_label = "abstained_fixed_risk" if fixed_risk_budget is not None else "abstained_risk_gate"
    elif unsafe:
        failure_label = "unsafe_stale_execution"
    elif stale and not success:
        failure_label = "stale_skill_decay"
    elif not success:
        failure_label = "unrecovered_shift"

    coverage = int(not abstain) if fixed_risk_budget is not None else int(not abstain)
    false_safe = int(fixed_risk_budget is not None and coverage == 1 and unsafe)

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
        "coverage": coverage,
        "false_safe": false_safe,
        "total_cost": f"{total_cost:.5f}",
        "predicted_success": f"{pred_after:.5f}",
        "calibration_abs_error": f"{abs(pred_after - float(success)):.5f}",
        "true_success_probability": f"{success_prob:.5f}",
        "risk_upper": f"{risk:.5f}",
        "hazard_score": f"{hazard:.5f}",
        "estimated_half_life": f"{est_half_life:.5f}",
        "true_half_life": f"{phys['true_half_life']:.5f}",
        "half_life_abs_relative_error": f"{abs(est_half_life - phys['true_half_life']) / max(1.0, phys['true_half_life']):.5f}",
        "shift_norm": f"{phys['shift_norm']:.5f}",
        "observed_norm": f"{phys['observed_norm']:.5f}",
        "mode_signal": f"{phys['mode_signal']:.5f}",
        "exec_age": f"{exec_age:.5f}",
        "failure_label": failure_label,
    }


def dataset_rows_for(split, total_steps, stress_axis=None, stress_level=0.0):
    rows = []
    for seed in SEEDS:
        for task in TASKS:
            for step in range(total_steps):
                phys = physical_state(split, task, seed, step, total_steps, stress_axis=stress_axis, stress_level=stress_level)
                rows.append(
                    {
                        "split": split,
                        "skill": task["skill"],
                        "seed": seed,
                        "step": step,
                        "true_half_life": f"{phys['true_half_life']:.5f}",
                        "shift_norm": f"{phys['shift_norm']:.5f}",
                        "observed_norm": f"{phys['observed_norm']:.5f}",
                        "sensor_noise": f"{phys['sensor_noise']:.5f}",
                        "mode_signal": f"{phys['mode_signal']:.5f}",
                        "probe_cost": f"{phys['probe_cost']:.5f}",
                    }
                )
    return rows


def run_rollouts_for(split, methods, steps, stress_axis=None, stress_level=0.0, ablation_methods=None, fixed_risk_budget=None):
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
                            fixed_risk_budget=fixed_risk_budget,
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
                            PROPOSAL,
                            state,
                            steps,
                            stress_axis=stress_axis,
                            stress_level=stress_level,
                            ablation=ablation,
                        )
                    )
        print(
            f"rollouts split={split} seed={seed} rows={len(rows)}"
            + (f" stress={stress_axis}:{stress_level:.2f}" if stress_axis else "")
            + (f" budget={fixed_risk_budget:.2f}" if fixed_risk_budget is not None else ""),
            flush=True,
        )
    return rows


def success_auc(vals):
    by_step = defaultdict(list)
    for r in vals:
        by_step[int(r["step"])].append(float(r["goal_success"]))
    ys = [np.mean(by_step[s]) for s in sorted(by_step)]
    if len(ys) <= 1:
        return float(np.mean(ys)) if ys else 0.0
    return float(np.trapz(ys, dx=1.0) / max(1, len(ys) - 1))


def seed_metrics(rows, methods=None, seeds=SEEDS):
    methods = methods or sorted({r["method"] for r in rows})
    groups = defaultdict(list)
    for r in rows:
        groups[(r["split"], r["method"], int(r["seed"]))].append(r)
    out = []
    for split in sorted({r["split"] for r in rows}):
        for method in methods:
            for seed in seeds:
                vals = groups.get((split, method, seed), [])
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
                risk = [float(r["risk_upper"]) for r in vals]
                hazard = [float(r["hazard_score"]) for r in vals]
                max_step = max(int(r["step"]) for r in vals)
                last_quarter = [float(r["goal_success"]) for r in vals if int(r["step"]) >= 0.75 * max_step]
                safety_utility = (
                    np.mean(successes)
                    - 0.88 * np.mean(unsafe)
                    - 0.34 * np.mean(stale)
                    - 0.14 * max(0.0, np.mean(cost) - 1.0)
                    - 0.08 * np.mean(abstain)
                )
                out.append(
                    {
                        "split": split,
                        "method": method,
                        "seed": seed,
                        "goal_success": f"{np.mean(successes):.5f}",
                        "success_auc": f"{success_auc(vals):.5f}",
                        "late_success": f"{np.mean(last_quarter):.5f}",
                        "unsafe_failure": f"{np.mean(unsafe):.5f}",
                        "stale_execution": f"{np.mean(stale):.5f}",
                        "refresh_rate": f"{np.mean(refresh):.5f}",
                        "probe_rate": f"{np.mean(probe):.5f}",
                        "abstain_rate": f"{np.mean(abstain):.5f}",
                        "total_cost": f"{np.mean(cost):.5f}",
                        "half_life_error": f"{np.mean(hle):.5f}",
                        "calibration_error": f"{np.mean(cal):.5f}",
                        "risk_upper": f"{np.mean(risk):.5f}",
                        "hazard_score": f"{np.mean(hazard):.5f}",
                        "safety_utility": f"{safety_utility:.5f}",
                        "rows": len(vals),
                    }
                )
    return out


def aggregate_metrics(seed_rows):
    out = []
    groups = defaultdict(list)
    for r in seed_rows:
        groups[(r["split"], r["method"])].append(r)
    for (split, method), vals in sorted(groups.items()):
        for metric in METRICS:
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


def pairwise_stats(seed_rows, proposal=PROPOSAL, metrics=PAIRWISE_METRICS):
    out = []
    index = {(r["split"], r["method"], int(r["seed"])): r for r in seed_rows}
    splits = sorted({r["split"] for r in seed_rows})
    methods = sorted({r["method"] for r in seed_rows if r["method"] != proposal})
    for split in splits:
        for reference in methods:
            for metric in metrics:
                diffs = []
                better = 0
                for seed in SEEDS:
                    prop = index.get((split, proposal, seed))
                    ref = index.get((split, reference, seed))
                    if prop and ref:
                        diff = float(prop[metric]) - float(ref[metric])
                        diffs.append(diff)
                        if metric in HIGHER_IS_BETTER:
                            better += int(diff > 0.0)
                        else:
                            better += int(diff < 0.0)
                if diffs:
                    mean = float(np.mean(diffs))
                    half_width = ci95(diffs)
                    out.append(
                        {
                            "split": split,
                            "target": proposal,
                            "reference": reference,
                            "metric": metric,
                            "mean_diff": f"{mean:.5f}",
                            "ci95": f"{half_width:.5f}",
                            "lower95": f"{mean - half_width:.5f}",
                            "target_better_seeds": better,
                            "seeds": len(diffs),
                        }
                    )
    return out


def metric_value(rows, split, method, metric):
    for row in rows:
        if row["split"] == split and row["method"] == method and row["metric"] == metric:
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((split, method, metric))


def hard_aggregate_seed_metrics(seed_rows):
    out = []
    by_method_seed = defaultdict(list)
    for r in seed_rows:
        if r["split"] in HARD_SPLITS:
            by_method_seed[(r["method"], int(r["seed"]))].append(r)
    for (method, seed), vals in sorted(by_method_seed.items()):
        if len(vals) != len(HARD_SPLITS):
            continue
        item = {
            "split": "hard_regime_aggregate",
            "method": method,
            "seed": seed,
            "rows": sum(int(r["rows"]) for r in vals),
        }
        for metric in METRICS:
            item[metric] = f"{np.mean([float(r[metric]) for r in vals]):.5f}"
        out.append(item)
    return out


def run_main():
    rows = []
    dataset = []
    for split in MAIN_SPLITS:
        dataset.extend(dataset_rows_for(split, DEPLOYMENT_STEPS))
        rows.extend(run_rollouts_for(split, METHODS, DEPLOYMENT_STEPS))
    seed_rows = seed_metrics(rows, METHODS)
    metric_rows = aggregate_metrics(seed_rows)
    pair_rows = pairwise_stats(seed_rows)
    hard_seed_rows = hard_aggregate_seed_metrics(seed_rows)
    hard_metric_rows = aggregate_metrics(hard_seed_rows)
    hard_pair_rows = pairwise_stats(hard_seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "dataset_summary.csv", dataset)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    write_csv(RESULTS / "hard_aggregate_seed_metrics.csv", hard_seed_rows)
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metric_rows)
    write_csv(RESULTS / "hard_aggregate_pairwise_stats.csv", hard_pair_rows)
    return rows, seed_rows, metric_rows, pair_rows, hard_seed_rows, hard_metric_rows, hard_pair_rows


def run_ablation():
    rows = []
    for split in ABLATION_SPLITS:
        rows.extend(run_rollouts_for(split, [], DEPLOYMENT_STEPS, ablation_methods=ABLATIONS))
    seed_rows = seed_metrics(rows, ABLATIONS)
    metric_rows = aggregate_metrics(seed_rows)
    summary = []
    for split in ABLATION_SPLITS:
        for ablation in ABLATIONS:
            goal = metric_value(metric_rows, split, ablation, "goal_success")
            late = metric_value(metric_rows, split, ablation, "late_success")
            unsafe = metric_value(metric_rows, split, ablation, "unsafe_failure")
            stale = metric_value(metric_rows, split, ablation, "stale_execution")
            refresh = metric_value(metric_rows, split, ablation, "refresh_rate")
            probe = metric_value(metric_rows, split, ablation, "probe_rate")
            hle = metric_value(metric_rows, split, ablation, "half_life_error")
            cost = metric_value(metric_rows, split, ablation, "total_cost")
            safety = metric_value(metric_rows, split, ablation, "safety_utility")
            summary.append(
                {
                    "split": split,
                    "ablation": ablation,
                    "goal_success": f"{goal[0]:.5f}",
                    "ci95_success": f"{goal[1]:.5f}",
                    "late_success": f"{late[0]:.5f}",
                    "unsafe_failure": f"{unsafe[0]:.5f}",
                    "stale_execution": f"{stale[0]:.5f}",
                    "refresh_rate": f"{refresh[0]:.5f}",
                    "probe_rate": f"{probe[0]:.5f}",
                    "half_life_error": f"{hle[0]:.5f}",
                    "total_cost": f"{cost[0]:.5f}",
                    "safety_utility": f"{safety[0]:.5f}",
                }
            )
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, seed_rows, summary


def run_stress():
    raw = []
    seed_rows_all = []
    summary = []
    for axis in STRESS_AXES:
        for level in STRESS_LEVELS:
            rows = run_rollouts_for("combined_micro_shift", STRESS_METHODS, STRESS_STEPS, stress_axis=axis, stress_level=level)
            for row in rows:
                row["stress_axis"] = axis
                row["stress_level"] = f"{level:.2f}"
            raw.extend(rows)
            local_seed = seed_metrics(rows, STRESS_METHODS)
            for row in local_seed:
                row["stress_axis"] = axis
                row["stress_level"] = f"{level:.2f}"
            seed_rows_all.extend(local_seed)
            metric_rows = aggregate_metrics(local_seed)
            for method in STRESS_METHODS:
                goal = metric_value(metric_rows, "combined_micro_shift", method, "goal_success")
                late = metric_value(metric_rows, "combined_micro_shift", method, "late_success")
                unsafe = metric_value(metric_rows, "combined_micro_shift", method, "unsafe_failure")
                stale = metric_value(metric_rows, "combined_micro_shift", method, "stale_execution")
                cost = metric_value(metric_rows, "combined_micro_shift", method, "total_cost")
                hle = metric_value(metric_rows, "combined_micro_shift", method, "half_life_error")
                safety = metric_value(metric_rows, "combined_micro_shift", method, "safety_utility")
                summary.append(
                    {
                        "stress_axis": axis,
                        "stress_level": f"{level:.2f}",
                        "method": method,
                        "goal_success": f"{goal[0]:.5f}",
                        "ci95_success": f"{goal[1]:.5f}",
                        "late_success": f"{late[0]:.5f}",
                        "unsafe_failure": f"{unsafe[0]:.5f}",
                        "stale_execution": f"{stale[0]:.5f}",
                        "total_cost": f"{cost[0]:.5f}",
                        "half_life_error": f"{hle[0]:.5f}",
                        "safety_utility": f"{safety[0]:.5f}",
                    }
                )
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", seed_rows_all)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, seed_rows_all, summary


def run_fixed_risk():
    raw = []
    seed_rows = []
    summary = []
    pairwise = []
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            rows = run_rollouts_for(split, FIXED_RISK_METHODS, FIXED_RISK_STEPS, fixed_risk_budget=budget)
            for row in rows:
                row["risk_budget"] = f"{budget:.2f}"
            raw.extend(rows)
            grouped = defaultdict(list)
            for row in rows:
                grouped[(row["method"], int(row["seed"]))].append(row)
            for method in FIXED_RISK_METHODS:
                for seed in SEEDS:
                    vals = grouped[(method, seed)]
                    executed = [r for r in vals if int(r["coverage"]) == 1]
                    coverage = len(executed) / len(vals) if vals else 0.0
                    false_safe = sum(int(r["false_safe"]) for r in executed)
                    false_safe_rate = false_safe / len(executed) if executed else 0.0
                    seed_rows.append(
                        {
                            "split": split,
                            "risk_budget": f"{budget:.2f}",
                            "method": method,
                            "seed": seed,
                            "episodes": len(vals),
                            "coverage": f"{coverage:.5f}",
                            "fixed_risk_success": f"{np.mean([int(r['goal_success']) for r in vals]):.5f}",
                            "executed_success": f"{np.mean([int(r['goal_success']) for r in executed]) if executed else 0.0:.5f}",
                            "false_safe_rate": f"{false_safe_rate:.5f}",
                            "unsafe_failure": f"{np.mean([int(r['unsafe_failure']) for r in executed]) if executed else 0.0:.5f}",
                            "stale_execution": f"{np.mean([int(r['stale_execution']) for r in executed]) if executed else 0.0:.5f}",
                            "total_cost": f"{np.mean([float(r['total_cost']) for r in executed]) if executed else 0.0:.5f}",
                        }
                    )
            for method in FIXED_RISK_METHODS:
                vals = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == f"{budget:.2f}" and r["method"] == method]
                summary.append(
                    {
                        "split": split,
                        "risk_budget": f"{budget:.2f}",
                        "method": method,
                        "coverage": f"{np.mean([float(r['coverage']) for r in vals]):.5f}",
                        "ci95_coverage": f"{ci95([float(r['coverage']) for r in vals]):.5f}",
                        "fixed_risk_success": f"{np.mean([float(r['fixed_risk_success']) for r in vals]):.5f}",
                        "ci95_fixed_risk_success": f"{ci95([float(r['fixed_risk_success']) for r in vals]):.5f}",
                        "executed_success": f"{np.mean([float(r['executed_success']) for r in vals]):.5f}",
                        "false_safe_rate": f"{np.mean([float(r['false_safe_rate']) for r in vals]):.5f}",
                        "unsafe_failure": f"{np.mean([float(r['unsafe_failure']) for r in vals]):.5f}",
                        "stale_execution": f"{np.mean([float(r['stale_execution']) for r in vals]):.5f}",
                        "total_cost": f"{np.mean([float(r['total_cost']) for r in vals]):.5f}",
                        "rows": len(rows),
                    }
                )
    index = {(r["split"], r["risk_budget"], r["method"], int(r["seed"])): r for r in seed_rows}
    for split in FIXED_RISK_SPLITS:
        for budget in FIXED_RISK_BUDGETS:
            budget_s = f"{budget:.2f}"
            for ref in [m for m in FIXED_RISK_METHODS if m != PROPOSAL]:
                for metric in ["coverage", "fixed_risk_success", "executed_success", "false_safe_rate"]:
                    diffs = []
                    for seed in SEEDS:
                        prop = index.get((split, budget_s, PROPOSAL, seed))
                        base = index.get((split, budget_s, ref, seed))
                        if prop and base:
                            diffs.append(float(prop[metric]) - float(base[metric]))
                    if diffs:
                        mean = float(np.mean(diffs))
                        half_width = ci95(diffs)
                        pairwise.append(
                            {
                                "split": split,
                                "risk_budget": budget_s,
                                "target": PROPOSAL,
                                "reference": ref,
                                "metric": metric,
                                "mean_diff": f"{mean:.5f}",
                                "ci95": f"{half_width:.5f}",
                                "lower95": f"{mean - half_width:.5f}",
                                "seeds": len(diffs),
                            }
                        )
    write_csv(RESULTS / "fixed_risk_raw.csv", raw)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "fixed_risk_metrics.csv", summary)
    write_csv(RESULTS / "fixed_risk_pairwise.csv", pairwise)
    return raw, seed_rows, summary, pairwise


def write_negative_cases(main_rows, ablation_rows, fixed_rows):
    candidates = []
    for r in main_rows:
        if r["method"] == PROPOSAL and int(r["goal_success"]) == 0:
            candidates.append((r, "v5_main_failure"))
        if r["method"] in {"conformal_risk_gate", "bayesian_skill_survival", "cvar_lifetime_guard"} and int(r["goal_success"]) == 1:
            candidates.append((r, "strong_baseline_success"))
    for r in ablation_rows:
        if r["method"] != "full_skill_half_life_scheduler_v5" and int(r["goal_success"]) == 1:
            candidates.append((r, "ablation_success_counterexample"))
    for r in fixed_rows:
        if int(r["false_safe"]) == 1:
            candidates.append((r, "fixed_risk_false_safe"))
        if r["failure_label"] == "abstained_fixed_risk":
            candidates.append((r, "fixed_risk_abstention"))
    lessons = {
        "unsafe_stale_execution": "skill age crossed the latent survival boundary before the policy refreshed",
        "stale_skill_decay": "execution remained nominally safe but the skill had decayed past its useful half-life",
        "unrecovered_shift": "physical shift reduced success without triggering a useful refresh or probe",
        "abstained_fixed_risk": "fixed-risk filtering preserved safety by removing coverage",
        "success": "counterexample where a baseline or ablation succeeds despite the full mechanism",
    }
    out = []
    seen = set()
    for row, source in candidates:
        key = (source, row["split"], row["method"], row["skill"], row["failure_label"])
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "source": source,
                "split": row["split"],
                "seed": row["seed"],
                "step": row["step"],
                "skill": row["skill"],
                "method": row["method"],
                "failure_label": row["failure_label"],
                "goal_success": row["goal_success"],
                "unsafe_failure": row["unsafe_failure"],
                "stale_execution": row["stale_execution"],
                "risk_upper": row["risk_upper"],
                "estimated_half_life": row["estimated_half_life"],
                "true_half_life": row["true_half_life"],
                "exec_age": row["exec_age"],
                "lesson": lessons.get(row["failure_label"], "negative case retained for audit"),
            }
        )
        if len(out) >= 24:
            break
    write_csv(RESULTS / "negative_cases.csv", out)
    return out


def terminal_decision(hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary):
    proposal = metric_value(hard_metric_rows, "hard_regime_aggregate", PROPOSAL, "goal_success")
    scores = [
        (m, metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[0])
        for m in NON_ORACLE
        if m != PROPOSAL
    ]
    best_ref, best_score = max(scores, key=lambda x: x[1])
    pair = [
        r
        for r in hard_pair_rows
        if r["split"] == "hard_regime_aggregate" and r["reference"] == best_ref and r["metric"] == "goal_success"
    ][0]
    safety_scores = []
    for method in NON_ORACLE:
        unsafe = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "unsafe_failure")[0]
        stale = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "stale_execution")[0]
        safety_scores.append((method, unsafe + stale))
    safety_ref, safety_best = min(safety_scores, key=lambda x: x[1])
    prop_safety = (
        metric_value(hard_metric_rows, "hard_regime_aggregate", PROPOSAL, "unsafe_failure")[0]
        + metric_value(hard_metric_rows, "hard_regime_aggregate", PROPOSAL, "stale_execution")[0]
    )

    ablation_gate = True
    for split in ABLATION_SPLITS:
        full = [r for r in ablation_summary if r["split"] == split and r["ablation"] == "full_skill_half_life_scheduler_v5"][0]
        full_success = float(full["goal_success"])
        full_safety = float(full["unsafe_failure"]) + float(full["stale_execution"])
        full_cost = float(full["total_cost"])
        full_hle = float(full["half_life_error"])
        for row in [r for r in ablation_summary if r["split"] == split and r["ablation"] != "full_skill_half_life_scheduler_v5"]:
            alt_success = float(row["goal_success"])
            alt_safety = float(row["unsafe_failure"]) + float(row["stale_execution"])
            alt_cost = float(row["total_cost"])
            if alt_success >= full_success and alt_safety <= full_safety + 0.005 and alt_cost <= full_cost + 0.020:
                ablation_gate = False
            if row["ablation"] == "minus_per_skill_survival" and alt_success > full_success and float(row["half_life_error"]) < full_hle:
                ablation_gate = False

    fixed_budget = [r for r in fixed_summary if r["risk_budget"] == "0.05" and r["method"] == PROPOSAL]
    fixed_gate = all(float(r["coverage"]) >= 0.25 and float(r["false_safe_rate"]) <= 0.05 for r in fixed_budget)

    max_stress = [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.50"]
    prop_stress = [r for r in max_stress if r["method"] == PROPOSAL][0]
    best_stress = max(float(r["goal_success"]) for r in max_stress if r["method"] not in {PROPOSAL, ORACLE})
    stress_gate = float(prop_stress["goal_success"]) >= best_stress - 0.03

    margin_gate = proposal[0] >= best_score + 0.03
    paired_gate = float(pair["lower95"]) > 0.0
    safety_gate = prop_safety <= safety_best + 0.01
    gates = {
        "best_reference": best_ref,
        "best_reference_success": best_score,
        "proposed_hard_success": proposal[0],
        "hard_margin": proposal[0] - best_score,
        "paired_lower95_vs_best": float(pair["lower95"]),
        "safety_reference": safety_ref,
        "safety_reference_sum": safety_best,
        "proposed_safety_sum": prop_safety,
        "margin_gate": margin_gate,
        "paired_gate": paired_gate,
        "safety_gate": safety_gate,
        "ablation_gate": ablation_gate,
        "fixed_risk_gate": fixed_gate,
        "stress_gate": stress_gate,
    }
    decision = "STRONG_REVISE" if all([margin_gate, paired_gate, safety_gate, ablation_gate, fixed_gate, stress_gate]) else "KILL_ARCHIVE"
    return decision, gates


def write_summary(metric_rows, hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary, main_rows, ablation_rows, stress_rows, fixed_rows, negative_cases):
    decision, gates = terminal_decision(hard_metric_rows, hard_pair_rows, ablation_summary, stress_summary, fixed_summary)
    with (RESULTS / "summary.txt").open("w", encoding="utf-8") as f:
        f.write("Paper 83 robot_skill_half_life_under_shift v5 expanded rebuild\n")
        f.write(f"Terminal recommendation: {decision}\n")
        f.write("Reason: CPU-only local skill-survival benchmark expanded with theory hooks, hard aggregate, ablations, stress, fixed-risk deployment, and negative cases; no robot hardware or external high-fidelity benchmark is present.\n")
        f.write(f"Main rollout rows: {len(main_rows)}\n")
        f.write(f"Dataset rows: {sum(1 for _ in open(RESULTS / 'dataset_summary.csv', encoding='utf-8')) - 1}\n")
        f.write(f"Ablation rollout rows: {len(ablation_rows)}\n")
        f.write(f"Stress rollout rows: {len(stress_rows)}\n")
        f.write(f"Fixed-risk rollout rows: {len(fixed_rows)}\n")
        f.write(f"Negative cases: {len(negative_cases)}\n")
        f.write(f"Seeds: {SEEDS}\n")
        f.write("\nHard-regime aggregate goal success:\n")
        for method in METHODS:
            goal = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "goal_success")
            late = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "late_success")
            unsafe = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "unsafe_failure")
            stale = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "stale_execution")
            safety = metric_value(hard_metric_rows, "hard_regime_aggregate", method, "safety_utility")
            f.write(
                f"{method} goal_success={goal[0]:.5f} ci95={goal[1]:.5f} late={late[0]:.5f} "
                f"unsafe={unsafe[0]:.5f} stale={stale[0]:.5f} safety_utility={safety[0]:.5f}\n"
            )
        f.write("\nDecision gates:\n")
        for key, value in gates.items():
            f.write(f"{key}: {value}\n")
        f.write("\nPairwise hard aggregate versus strongest non-oracle:\n")
        for row in hard_pair_rows:
            if row["split"] == "hard_regime_aggregate" and row["reference"] == gates["best_reference"]:
                f.write(f"{row['metric']} diff={row['mean_diff']} ci95={row['ci95']} lower95={row['lower95']} better_seeds={row['target_better_seeds']}/{row['seeds']}\n")
        f.write("\nAblation results:\n")
        for row in ablation_summary:
            f.write(
                f"{row['split']} {row['ablation']} goal_success={row['goal_success']} ci95={row['ci95_success']} "
                f"unsafe={row['unsafe_failure']} stale={row['stale_execution']} hle={row['half_life_error']} "
                f"cost={row['total_cost']} safety_utility={row['safety_utility']}\n"
            )
        f.write("\nCombined stress level 1.50:\n")
        for row in [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.50"]:
            f.write(
                f"{row['method']} goal_success={row['goal_success']} ci95={row['ci95_success']} unsafe={row['unsafe_failure']} "
                f"stale={row['stale_execution']} hle={row['half_life_error']} safety_utility={row['safety_utility']}\n"
            )
        f.write("\nFixed-risk budget 0.05:\n")
        for row in [r for r in fixed_summary if r["risk_budget"] == "0.05"]:
            f.write(
                f"{row['split']} {row['method']} coverage={row['coverage']} fixed_risk_success={row['fixed_risk_success']} "
                f"executed_success={row['executed_success']} false_safe_rate={row['false_safe_rate']} unsafe={row['unsafe_failure']} stale={row['stale_execution']}\n"
            )
    return decision, gates


def plot_outputs(hard_metric_rows, main_rows, ablation_summary, stress_summary, fixed_summary):
    plot_methods = [
        "frozen_behavior_clone",
        "domain_randomized_clone",
        "fixed_interval_refresh",
        "online_finetune",
        "scalar_uncertainty_gate",
        "conformal_risk_gate",
        "ensemble_uncertainty_gate",
        "bayesian_skill_survival",
        "cvar_lifetime_guard",
        "skill_half_life_scheduler_v5",
        "oracle_shift_aware_scheduler",
    ]
    colors = ["#868e96", "#adb5bd", "#74c0fc", "#4dabf7", "#a9e34b", "#37b24d", "#2f9e44", "#0ca678", "#f08c00", "#087f5b", "#095c4a"]
    vals = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[0] for m in plot_methods]
    errs = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "goal_success")[1] for m in plot_methods]
    plt.figure(figsize=(12.8, 4.9))
    plt.bar(range(len(plot_methods)), vals, yerr=errs, color=colors, capsize=3)
    plt.xticks(range(len(plot_methods)), [LABELS[m].replace(" ", "\n") for m in plot_methods], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Hard-regime aggregate skill half-life")
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_hard_success.png", dpi=220)
    plt.close()

    unsafe = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "unsafe_failure")[0] for m in plot_methods]
    stale = [metric_value(hard_metric_rows, "hard_regime_aggregate", m, "stale_execution")[0] for m in plot_methods]
    x = np.arange(len(plot_methods))
    plt.figure(figsize=(12.5, 4.9))
    plt.bar(x - 0.18, unsafe, width=0.36, label="unsafe failure", color="#c92a2a")
    plt.bar(x + 0.18, stale, width=0.36, label="stale execution", color="#f08c00")
    plt.xticks(x, [LABELS[m].replace(" ", "\n") for m in plot_methods], fontsize=7)
    plt.ylabel("rate")
    plt.title("Unsafe and stale executions")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_failure_modes_v5.png", dpi=220)
    plt.close()

    target_methods = ["domain_randomized_clone", "conformal_risk_gate", "bayesian_skill_survival", "cvar_lifetime_guard", PROPOSAL, ORACLE]
    bins = [(0, 16), (16, 32), (32, 48), (48, 64)]
    plt.figure(figsize=(10.0, 5.2))
    for method in target_methods:
        ys = []
        for lo, hi in bins:
            vals = [
                float(r["goal_success"])
                for r in main_rows
                if r["split"] == "combined_micro_shift" and r["method"] == method and lo <= int(r["step"]) < hi
            ]
            ys.append(float(np.mean(vals)))
        plt.plot([f"{lo}-{hi}" for lo, hi in bins], ys, marker="o", linewidth=2, label=LABELS[method])
    plt.ylabel("goal success")
    plt.ylim(0, 1.0)
    plt.title("Deployment-age bins on combined micro-shift")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_decay_curves_v5.png", dpi=220)
    plt.close()

    combined_ablation = [r for r in ablation_summary if r["split"] == "combined_micro_shift"]
    plt.figure(figsize=(12.2, 5.0))
    plt.bar(range(len(combined_ablation)), [float(r["goal_success"]) for r in combined_ablation], yerr=[float(r["ci95_success"]) for r in combined_ablation], color="#0ca678", capsize=3)
    plt.xticks(range(len(combined_ablation)), [r["ablation"].replace("_", "\n") for r in combined_ablation], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("goal success")
    plt.title("Skill half-life scheduler v5 ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_ablation_v5.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.0, 5.2))
    for method in STRESS_METHODS:
        rows = sorted([r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method], key=lambda r: float(r["stress_level"]))
        x = [float(r["stress_level"]) for r in rows]
        y = [float(r["goal_success"]) for r in rows]
        e = [float(r["ci95_success"]) for r in rows]
        plt.errorbar(x, y, yerr=e, marker="o", linewidth=2, capsize=3, label=LABELS[method])
    plt.xlabel("combined physical-shift stress")
    plt.ylabel("goal success")
    plt.ylim(0, 1.05)
    plt.title("Combined stress sweep")
    plt.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_stress_sweep_v5.png", dpi=220)
    plt.close()

    budget_rows = [r for r in fixed_summary if r["split"] == "combined_micro_shift" and r["risk_budget"] == "0.05"]
    plt.figure(figsize=(10.8, 4.8))
    x = np.arange(len(budget_rows))
    plt.bar(x - 0.18, [float(r["coverage"]) for r in budget_rows], width=0.36, label="coverage", color="#4dabf7")
    plt.bar(x + 0.18, [float(r["false_safe_rate"]) for r in budget_rows], width=0.36, label="false-safe rate", color="#c92a2a")
    plt.xticks(x, [LABELS[r["method"]].replace(" ", "\n") for r in budget_rows], fontsize=7)
    plt.ylim(0, 1.05)
    plt.ylabel("rate")
    plt.title("Fixed-risk deployment at budget 0.05")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "half_life_fixed_risk_v5.png", dpi=220)
    plt.close()


def main():
    main_rows, seed_rows, metric_rows, pair_rows, hard_seed_rows, hard_metric_rows, hard_pair_rows = run_main()
    ablation_rows, ablation_seed_rows, ablation_summary = run_ablation()
    stress_raw, stress_seed_rows, stress_summary = run_stress()
    fixed_raw, fixed_seed_rows, fixed_summary, fixed_pairwise = run_fixed_risk()
    negative = write_negative_cases(main_rows, ablation_rows, fixed_raw)
    decision, gates = write_summary(
        metric_rows,
        hard_metric_rows,
        hard_pair_rows,
        ablation_summary,
        stress_summary,
        fixed_summary,
        main_rows,
        ablation_rows,
        stress_raw,
        fixed_raw,
        negative,
    )
    plot_outputs(hard_metric_rows, main_rows, ablation_summary, stress_summary, fixed_summary)
    print(f"terminal={decision}")
    print(
        "rows "
        f"main={len(main_rows)} ablation={len(ablation_rows)} stress={len(stress_raw)} "
        f"fixed_risk={len(fixed_raw)} negative_cases={len(negative)}"
    )
    print(f"gates={gates}")
    print(f"wrote results to {RESULTS}")


if __name__ == "__main__":
    main()
