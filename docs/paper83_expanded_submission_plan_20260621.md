# Paper 83 Expanded Submission-Readiness Plan - 2026-06-21

## Objective

Rebuild Paper 83, `robot_skill_half_life_under_shift`, into the strongest honest ICLR-main-target manuscript possible under the current constraints: CPU-only, RAM-light, no fabricated robot hardware evidence, no Desktop PDFs, numbered final PDF in Downloads only, public GitHub repo, and bright boxed clickable citations. The rebuild must add real theory, a stronger experiment suite, fixed-risk deployment checks, ablations, stress tests, negative cases, and a 25+ page manuscript without filler.

The v4 record is negative: the half-life scheduler is statistically indistinguishable from a conformal risk gate on the combined micro-shift split, and removing per-skill survival improves success. The v5 pass may revise the method, but the final protocol below is frozen before execution and all predefined results must be reported honestly.

## Method Upgrade To Test

The v5 method is `skill_half_life_scheduler_v5`, a calibrated skill-survival scheduler. For each skill under physical shift it estimates:

- latent deployment age;
- true and observed physical shift components;
- per-skill survival half-life;
- hazard margin to a refresh boundary;
- probe value under uncertainty;
- refresh/abstain value under unsafe stale execution risk;
- uncertainty-adjusted risk upper bound from observed shift and sensor noise.

The manuscript will state a theory layer around skill survival:

- define skill survival, hazard, deployment half-life, stale execution, and fixed-risk coverage;
- prove an exponential-survival threshold lemma connecting half-life estimates to refresh decisions;
- prove a dominance proposition for refresh/probe/execute decisions when calibrated hazard and probe value are ordered;
- identify a negative identifiability theorem: if per-skill hazards collapse to a shared latent shift factor, per-skill survival modeling is unnecessary and may be beaten by scalar or conformal gates.

These are local modeling claims, not claims of robot deployment.

## Main Experiment Protocol

Run one deterministic CPU process, one paper at a time. Do not reduce seeds, splits, methods, or rows for convenience.

Main evaluation:

- seeds: 10 (`0..9`);
- deployment steps per split, seed, and skill: 64;
- skills: `pick_place`, `door_pull`, `drawer_slide`, `peg_insert`, and `cable_route`;
- splits: `nominal_slow_drift`, `friction_shift`, `payload_mass_shift`, `compliance_shift`, `sensor_noise_shift`, `contact_mode_chatter`, `probe_cost_shift`, and `combined_micro_shift`;
- methods: `frozen_behavior_clone`, `domain_randomized_clone`, `fixed_interval_refresh`, `online_finetune`, `scalar_uncertainty_gate`, `conformal_risk_gate`, `ensemble_uncertainty_gate`, `hazard_regression_refresh`, `bayesian_skill_survival`, `cvar_lifetime_guard`, `skill_half_life_scheduler_v5`, and `oracle_shift_aware_scheduler`;
- expected main rollout rows: `8 * 10 * 5 * 64 * 12 = 307,200`;
- expected dataset rows: `8 * 10 * 5 * 64 = 25,600`;
- produce seed metrics, aggregate metrics, paired statistics, hard-regime aggregate seed metrics, hard-regime aggregate metrics, and hard-regime paired statistics.

Hard-regime aggregate:

- include all non-nominal splits: `friction_shift`, `payload_mass_shift`, `compliance_shift`, `sensor_noise_shift`, `contact_mode_chatter`, `probe_cost_shift`, and `combined_micro_shift`;
- report goal success, late success, unsafe failure, stale execution, refresh/probe/abstain rates, total cost, half-life error, calibration error, risk upper bound, hazard score, and safety utility;
- compare v5 against the strongest non-oracle baseline by paired seed differences.

## Ablation Protocol

Run ablations on `combined_micro_shift` and `contact_mode_chatter`, 10 seeds, 64 deployment steps, and all five skills.

Ablations:

- `full_skill_half_life_scheduler_v5`;
- `minus_per_skill_survival`;
- `minus_probe_updates`;
- `minus_hazard_margin`;
- `minus_shift_decomposition`;
- `minus_uncertainty_calibration`;
- `minus_skill_age_state`;
- `fixed_global_half_life`;
- `threshold_only_risk_gate`;
- `expected_success_only`.

Expected ablation rows: `2 * 10 * 5 * 64 * 10 = 64,000`.

The mechanism gate fails if any central ablation matches or beats the full method on hard-split goal success without a safety or cost tradeoff, or if removing per-skill survival improves both success and half-life error.

## Stress Protocol

Run stress sweeps over five axes:

- drift rate;
- sensor noise;
- contact-mode chatter;
- probe cost;
- combined physical shift.

Use stress levels `0.00, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50`, 10 seeds, 32 steps, all five skills, and the seven stress methods:

- `domain_randomized_clone`;
- `conformal_risk_gate`;
- `ensemble_uncertainty_gate`;
- `bayesian_skill_survival`;
- `cvar_lifetime_guard`;
- `skill_half_life_scheduler_v5`;
- `oracle_shift_aware_scheduler`.

Expected stress rollout rows: `5 * 7 * 10 * 5 * 32 * 7 = 392,000`.

The stress gate fails if v5 is dominated by a non-oracle method at maximum combined stress, or if its unsafe/stale rate grows faster than the best learned or conformal baseline.

## Fixed-Risk Protocol

Evaluate safety-filtered deployment under unsafe-execution risk budgets `0.02`, `0.05`, `0.10`, and `0.20` on `combined_micro_shift` and `contact_mode_chatter`.

Candidate methods:

- `conformal_risk_gate`;
- `ensemble_uncertainty_gate`;
- `bayesian_skill_survival`;
- `cvar_lifetime_guard`;
- `skill_half_life_scheduler_v5`;
- `oracle_shift_aware_scheduler`.

Each method may abstain from executing if its estimated unsafe stale-execution risk exceeds the budget. Report coverage, fixed-risk success, executed success, false-safe rate, unsafe failure, stale execution, and cost.

Expected fixed-risk rows: `2 * 4 * 10 * 5 * 40 * 6 = 96,000`.

The fixed-risk gate fails if v5 cannot maintain false-safe rate below the budget while preserving meaningful coverage at budget `0.05`.

## Negative Cases

Retain at least 24 negative cases spanning:

- unsafe stale executions;
- high-confidence false-safe executions;
- hard contact-mode chatter failures;
- cases where a central ablation succeeds;
- cases where a strong baseline beats v5;
- fixed-risk abstentions that preserve safety but erase coverage.

The manuscript must include these cases as evidence against overclaiming.

## Decision Criteria

Mark `STRONG_REVISE` only if all local gates pass:

- v5 beats the strongest non-oracle baseline on the hard-regime aggregate by at least `0.03` absolute goal success;
- the paired lower confidence bound versus the strongest non-oracle baseline is positive;
- v5 does not increase unsafe failure plus stale execution versus the strongest safety baseline by more than `0.01`;
- fixed-risk coverage at budget `0.05` is at least `0.25` with false-safe rate not above budget;
- central ablations degrade success, safety, or cost, showing the score terms are necessary;
- maximum combined stress is not dominated by a non-oracle baseline.

Mark `KILL_ARCHIVE` if any gate fails. Do not mark the paper ICLR-main-ready without real robot evidence, recognized high-fidelity benchmark validation, released trained baselines, and manual expert prior-work vetting.

## Manuscript And Artifact Requirements

- Generate a 25+ page ICLR-style manuscript from frozen CSVs.
- Use bright boxed clickable citations via `hyperref` with visible citation borders.
- Include theory, protocol, main results, hard-regime aggregate, ablations, stress, fixed-risk deployment, negative cases, limitations, and reviewer-attack responses.
- Build the final numbered PDF only as `C:/Users/wangz/Downloads/83.pdf`.
- Do not copy any PDF to Desktop.
- Add a validator that checks expected row counts, page count, citation/link settings, unresolved references, PDF placement, Desktop exclusion, and SHA256.
- Commit and push all repository changes to the public GitHub repository.
- Update root `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, `MASTER_SUBMISSION_REPORT.md`, and `SUBMISSION_AUDIT_MATRIX.csv` before moving to Paper 84.
