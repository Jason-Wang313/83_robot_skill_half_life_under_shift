# Paper 83 Rebuild Plan

Last update: 2026-06-14 10:13:21 +01:00

## Target Claim

Robot skills have measurable deployment half-lives under small physical shifts. A planner that estimates per-skill survival curves should decide when to keep executing, probe, refresh, or abstain better than fixed refresh schedules, scalar uncertainty gates, and online fine-tuning.

## Evidence To Build

Implement a deterministic local skill-survival benchmark, not the v3 generic branch-mechanism scaffold.

### Splits

- `nominal_slow_drift`: mild gradual drift.
- `friction_shift`: contact friction changes across deployment.
- `payload_mass_shift`: payload mass and inertia drift.
- `compliance_shift`: tool/environment compliance changes.
- `combined_micro_shift`: all shifts combined with hidden mode flips.

### Skills

- planar pick-and-place.
- door pull.
- drawer slide.
- peg insertion.

### Methods

- `frozen_behavior_clone`
- `domain_randomized_clone`
- `fixed_interval_refresh`
- `online_finetune`
- `scalar_uncertainty_gate`
- `conformal_risk_gate`
- `skill_half_life_scheduler` (proposed)
- `oracle_shift_aware_scheduler`

### Main Metrics

- deployment success.
- success area under deployment curve.
- unsafe failure rate.
- stale execution rate.
- refresh/probe cost.
- half-life estimation error.
- calibrated survival error.
- paired seed-level differences versus strongest non-oracle baselines.

### Ablations

- full half-life scheduler.
- minus per-skill survival model.
- minus probe updates.
- minus hazard margin.
- minus shift decomposition.
- fixed global half-life.
- threshold-only risk gate.

### Stress Tests

- drift rate.
- sensor noise.
- hidden mode flip probability.
- probe cost.
- combined stress.

### Terminal Gate

Mark `STRONG_REVISE` only if the proposed scheduler beats the best non-oracle baseline on combined micro-shift success and success AUC, reduces unsafe failures, and ablations degrade the mechanism. Otherwise mark `KILL_ARCHIVE`.

Even a `STRONG_REVISE` result is not ICLR-main ready without hardware or recognized high-fidelity benchmark evidence.
