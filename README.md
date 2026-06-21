# 83 Robot Skill Half-Life Under Shift

Submission-hardening version: v5 expanded audit

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

Latest audit rerun: 2026-06-21.

This repository contains a reproducible local evidence audit for the research bet:

> Quantify how quickly robot skills decay under small physical environment shifts.

The v5 rebuild expands the archive into a deterministic skill-survival benchmark covering five skills, eight physical-shift splits, 12 methods, hard-regime aggregation, two-split ablations, five-axis stress sweeps, fixed-risk deployment, and retained negative cases.

## Why This Is Archived

- The 2026-06-21 rerun regenerated 307,200 main rollouts, 25,600 physical-state rows, 64,000 ablation rollouts, 392,000 stress rollouts, 96,000 fixed-risk rollouts, and 24 negative cases.
- On the predefined hard-regime aggregate, `skill_half_life_scheduler_v5` reaches `0.81638 +/- 0.00326` goal success.
- The strongest non-oracle baseline, `cvar_lifetime_guard`, reaches `0.82821 +/- 0.00378`.
- The paired hard-aggregate goal-success difference versus `cvar_lifetime_guard` is `-0.01183 +/- 0.00345`, with lower95 `-0.01528`.
- The method fails the margin, paired, ablation, fixed-risk, and maximum-stress gates.
- At fixed-risk budget `0.05`, all non-oracle methods have zero coverage on both fixed-risk splits.
- The evidence is local and synthetic, not robot hardware or recognized high-fidelity simulator validation.

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
python ..\scripts\validate_submission_artifacts.py
```

The runner writes the complete CSV suite under `results/`, figures under `figures/`, and a 25+ page ICLR-style audit manuscript under `paper/`.

Canonical local PDF: `C:/Users/wangz/Downloads/83.pdf`

Validated PDF: 62 pages, SHA256 `33F4831CA807F4D47A799726E3E34CAE97CBEBD7DBFB63EC096965A663524628`.

No PDF should be copied to the visible Desktop.
