# Paper 83 Submission Readiness Audit v5

Last update: 2026-06-21

## Decision

`KILL_ARCHIVE` for ICLR main.

## Evidence Scale

- Main rollouts: 307,200.
- Dataset rows: 25,600.
- Main seed metrics: 960.
- Main aggregate metrics: 1,344.
- Main pairwise stats: 704.
- Hard aggregate seed metrics: 120.
- Hard aggregate metrics: 168.
- Hard aggregate pairwise stats: 88.
- Ablation rollouts: 64,000.
- Ablation seed metrics: 200.
- Ablation aggregate rows: 20.
- Stress rollouts: 392,000.
- Stress seed metrics: 2,450.
- Stress aggregate rows: 245.
- Fixed-risk rollouts: 96,000.
- Fixed-risk seed metrics: 480.
- Fixed-risk aggregate rows: 48.
- Fixed-risk pairwise rows: 160.
- Negative cases: 24.

## Submission Blockers

- The proposed method loses hard-regime goal success to `cvar_lifetime_guard`.
- The paired lower95 versus the strongest non-oracle baseline is negative.
- Contact-mode ablations beat the full mechanism.
- Fixed-risk coverage at budget `0.05` collapses to zero for non-oracle methods.
- Maximum combined stress is dominated by `bayesian_skill_survival`.
- Evidence remains local and synthetic; there is no real robot or recognized high-fidelity benchmark validation.

## Artifact Status

- `C:/Users/wangz/Downloads/83.pdf`: present, 62 pages, validated.
- `C:/Users/wangz/Desktop/83.pdf`: absent.
- Public GitHub repo: `https://github.com/Jason-Wang313/83_robot_skill_half_life_under_shift`.
