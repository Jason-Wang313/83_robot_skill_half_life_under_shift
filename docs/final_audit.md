# Final Audit

1. Chosen thesis: Robot Skill Half-Life Under Shift explores `Quantify how quickly skills decay under small physical environment shifts.` for continual robot learning.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v4.
4. Reason: a local skill-survival benchmark was added, but the half-life scheduler does not decisively beat conformal risk gating and a central ablation improves over the full mechanism.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, and `docs/hostile_reviewer_response.md`.
6. Reproducibility: v4 benchmark code runs and regenerates metrics/figures, but no real robot or high-fidelity benchmark is reproduced.
7. Claim-validity status: positive main-conference claims killed; v4 negative evidence audit retained.
8. Exact Downloads PDF path: `C:/Users/wangz/Downloads/83.pdf`
9. GitHub URL: https://github.com/Jason-Wang313/83_robot_skill_half_life_under_shift
10. Confirmation: no visible Desktop copy was requested or made.
11. 2026-06-15 rerun: 80,640 main rollouts, 14,112 ablation rollouts, and 201,600 stress rollouts reproduced `KILL_ARCHIVE`.
12. Hard-split gate: `skill_half_life_scheduler` vs `conformal_risk_gate` paired goal-success difference is `0.00248 +/- 0.02721`.
13. Mechanism gate: `minus_per_skill_survival` improves goal success to `0.80456`, above the full ablation scheduler at `0.79712`.
