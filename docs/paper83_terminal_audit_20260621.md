# Paper 83 Terminal Audit - 2026-06-21

## Terminal Decision

`KILL_ARCHIVE` for ICLR main.

## What Changed In v5

- Added a frozen expanded plan before execution.
- Expanded main evaluation to 10 seeds, five skills, eight splits, 12 methods, and 307,200 main rollouts.
- Added 25,600 physical-state rows for auditability.
- Added hard-regime aggregate metrics and paired hard-regime statistics.
- Added two-split ablations: 64,000 rollouts and 200 seed-level rows.
- Added five-axis stress sweeps: 392,000 rollouts, 2,450 seed-level rows, and 245 aggregate rows.
- Added fixed-risk deployment: 96,000 rollouts, 480 seed-level rows, 48 aggregate rows, and 160 pairwise rows.
- Retained 24 negative cases.
- Generated a 62-page ICLR-style PDF with bright boxed clickable citations.
- Validated `C:/Users/wangz/Downloads/83.pdf`; no Desktop PDF is present.

## Main Evidence

Hard-regime aggregate:

- `skill_half_life_scheduler_v5`: goal success `0.81638 +/- 0.00326`; unsafe `0.00281`; stale `0.00000`; safety utility `0.80158`.
- `cvar_lifetime_guard`: goal success `0.82821 +/- 0.00378`; unsafe `0.00156`; stale `0.00000`; safety utility `0.80829`.
- `bayesian_skill_survival`: goal success `0.82143 +/- 0.00351`; unsafe `0.00210`; stale `0.00000`; safety utility `0.80596`.
- Oracle upper bound: goal success `0.83594 +/- 0.00407`.

Paired hard aggregate versus the strongest non-oracle baseline, `cvar_lifetime_guard`:

- goal success diff `-0.01183 +/- 0.00345`; lower95 `-0.01528`; v5 better seeds `0/10`.
- safety utility diff `-0.00671 +/- 0.00370`; lower95 `-0.01041`; v5 better seeds `1/10`.

## Failed Gates

- `margin_gate`: false.
- `paired_gate`: false.
- `ablation_gate`: false.
- `fixed_risk_gate`: false.
- `stress_gate`: false.

The safety gate passes, but this is insufficient because the main, paired, ablation, fixed-risk, and stress evidence do not support the central claim.

## Fixed-Risk Evidence

At risk budget `0.05`, all non-oracle methods have zero coverage on both `combined_micro_shift` and `contact_mode_chatter`. The oracle retains only low coverage (`0.02700` and `0.03450`). This blocks any deployment-readiness claim.

## PDF Verification

- Canonical PDF: `C:/Users/wangz/Downloads/83.pdf`.
- Pages: 62.
- SHA256: `33F4831CA807F4D47A799726E3E34CAE97CBEBD7DBFB63EC096965A663524628`.
- Desktop PDF: absent.
- Validator: passed.
- Visual QA: rendered representative pages; citation boxes, table-reference boxes, figures, dense appendix tables, prior-work table, and references are readable.

## Final Rationale

Skill half-life under physical shift remains a useful research direction, but this v5 local benchmark does not support an ICLR-main submission. The method is competitive against weak baselines, but it loses to CVaR and Bayesian survival baselines, fails the paired hard-aggregate test, fails fixed-risk coverage, is contradicted by contact-mode ablations, and remains local synthetic evidence only.
