# Submission Version Log

## v1 - Generated Draft
- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening
- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/83.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive
- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats are not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Skill-Survival Evidence Audit
- Replaced the template scaffold with a deterministic local skill half-life benchmark.
- Added eight methods, four skills, five physical-shift splits, ablations, stress sweeps, negative cases, and figures.
- Main result: half-life scheduler is safe but statistically indistinguishable from conformal risk gating on combined micro-shift.
- Ablation result: removing per-skill survival improves over the full mechanism.
- Recompiled the canonical PDF with `Submission-hardening version: v4`.
- Terminal decision: KILL_ARCHIVE.

## v4.1 - 2026-06-15 Rerun Audit
- Added the paper-specific ICLR-main execution plan before running any new evidence.
- Re-ran `python src\run_experiment.py` from source and reproduced `terminal=KILL_ARCHIVE`.
- Verified 80,640 main rollouts, 14,112 ablation rollouts, 201,600 stress rollouts, seven seeds, eight methods, seven ablations, five stress axes, and four negative cases.
- Preserved the terminal decision because the paired gain over conformal risk gating remains negligible and the central ablation remains contradictory.
