# Paper 83 Terminal Audit

Date: 2026-06-15 09:02:54 +01:00

Paper: `83_robot_skill_half_life_under_shift`

Terminal decision: `KILL_ARCHIVE`

## Rerun Command

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
```

The experiment runner completed successfully and printed `terminal=KILL_ARCHIVE`.

## Evidence Coverage

- `rollouts.csv`: 80,640 rows, 22 columns.
- `raw_seed_metrics.csv`: 280 rows, 15 columns.
- `metrics.csv`: 440 rows, 7 columns.
- `pairwise_stats.csv`: 245 rows, 6 columns.
- `ablation_rollouts.csv`: 14,112 rows, 22 columns.
- `ablation_seed_metrics.csv`: 49 rows, 15 columns.
- `ablation_metrics.csv`: 7 rows, 10 columns.
- `stress_sweep_raw.csv`: 201,600 rows, 24 columns.
- `stress_sweep.csv`: 150 rows, 9 columns.
- `negative_cases.csv`: 4 rows, 4 columns.

Verified seeds: `0, 1, 2, 3, 4, 5, 6`.

Verified splits: `nominal_slow_drift`, `friction_shift`, `payload_mass_shift`, `compliance_shift`, `combined_micro_shift`.

Verified skills: `pick_place`, `door_pull`, `drawer_slide`, `peg_insert`.

Verified methods: `frozen_behavior_clone`, `domain_randomized_clone`, `fixed_interval_refresh`, `online_finetune`, `scalar_uncertainty_gate`, `conformal_risk_gate`, `skill_half_life_scheduler`, `oracle_shift_aware_scheduler`.

Verified ablations: `full_skill_half_life_scheduler`, `minus_per_skill_survival`, `minus_probe_updates`, `minus_hazard_margin`, `minus_shift_decomposition`, `fixed_global_half_life`, `threshold_only_risk_gate`.

Verified stress axes: `drift_rate`, `sensor_noise`, `mode_flip`, `probe_cost`, `combined`.

## Main Gate

Combined micro-shift goal success:

- `skill_half_life_scheduler`: `0.80059 +/- 0.01080`.
- `conformal_risk_gate`: `0.79811 +/- 0.01961`.
- Paired goal-success difference versus conformal gate: `0.00248 +/- 0.02721`.
- `oracle_shift_aware_scheduler`: `0.82937 +/- 0.01636`.

The proposed method is safer than the conformal gate on unsafe failures (`0.00099` vs `0.00397`) but does not produce a decisive success gain.

## Ablation Gate

- Full ablation scheduler: `0.79712 +/- 0.01168` goal success.
- `minus_per_skill_survival`: `0.80456 +/- 0.01799` goal success.
- Half-life error improves from `0.17594` to `0.13417` when per-skill survival is removed.

This contradicts the central mechanism claim.

## Stress Gate

At maximum combined stress:

- `skill_half_life_scheduler`: `0.79688 +/- 0.02747` goal success, `0.00074` unsafe failure.
- `conformal_risk_gate`: `0.79985 +/- 0.01953` goal success, `0.00372` unsafe failure.
- `oracle_shift_aware_scheduler`: `0.81920 +/- 0.01439` goal success.

Stress evidence does not rescue the central claim.

## Submission Decision

Paper 83 is not ICLR-main ready. It should remain an archived negative result unless future work adds real robot or recognized high-fidelity simulator evidence, learned survival models from deployment data, stronger implemented baselines, and decisive paired gains with mechanism-validating ablations.

## PDF Artifact

- Canonical PDF: `C:/Users/wangz/Downloads/83.pdf`.
- SHA256: `547AD30D755079C7999902C8EF77B5852B141D25AD95C748FD6617A82ADF089E`.
- Desktop copy: absent.
