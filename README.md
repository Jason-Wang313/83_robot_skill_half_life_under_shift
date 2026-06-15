# 83 Robot Skill Half-Life Under Shift

Submission-hardening version: v4

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

Latest audit rerun: 2026-06-15.

This repository contains a reproducible local evidence audit for the research bet:

> Quantify how quickly robot skills decay under small physical environment shifts.

The v4 rebuild replaces the template scaffold with a deterministic skill-survival benchmark covering four skills, five physical-shift splits, eight methods, ablations, stress sweeps, and negative cases.

## Why This Is Archived

- The 2026-06-15 rerun regenerated 80,640 main rollouts, 14,112 ablation rollouts, and 201,600 stress rollouts.
- On the combined micro-shift split, `skill_half_life_scheduler` reaches `0.80059 +/- 0.01080` goal success.
- The strongest non-oracle baseline, `conformal_risk_gate`, reaches `0.79811 +/- 0.01961`.
- The paired goal-success difference versus the conformal gate is only `0.00248 +/- 0.02721`.
- The `minus_per_skill_survival` ablation improves goal success to `0.80456 +/- 0.01799`, contradicting the central mechanism claim.
- The evidence is local and synthetic, not hardware or high-fidelity simulator validation.

## Reproduce

```powershell
python src\run_experiment.py
```

The runner writes:

- `results/rollouts.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep.csv`
- `results/negative_cases.csv`
- `results/summary.txt`
- `figures/half_life_*.png`

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/83.pdf`
