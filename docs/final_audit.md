# Final Audit

1. Chosen thesis: Robot Skill Half-Life Under Shift explores `Quantify how quickly skills decay under small physical environment shifts.` for continual robot learning.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v5 expanded.
4. Reason: the v5 method is competitive against weak baselines but loses hard-regime goal success to `cvar_lifetime_guard`, has a negative paired lower95, fails ablation necessity, has zero non-oracle fixed-risk coverage at budget `0.05`, and is dominated at maximum combined stress by `bayesian_skill_survival`.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, `docs/hostile_reviewer_response.md`, and the manuscript prior-work pressure table.
6. Reproducibility: v5 benchmark code regenerates all metrics/figures, but no real robot or recognized high-fidelity benchmark is reproduced.
7. Claim-validity status: positive main-conference claims killed; v5 negative evidence audit retained.
8. Exact Downloads PDF path: `C:/Users/wangz/Downloads/83.pdf`
9. PDF pages: 62.
10. PDF SHA256: `33F4831CA807F4D47A799726E3E34CAE97CBEBD7DBFB63EC096965A663524628`.
11. GitHub URL: https://github.com/Jason-Wang313/83_robot_skill_half_life_under_shift
12. Confirmation: no visible Desktop copy was requested or made.
13. 2026-06-21 rerun: 307,200 main rollouts, 25,600 dataset rows, 64,000 ablation rollouts, 392,000 stress rollouts, 96,000 fixed-risk rollouts, and 24 negative cases produced `KILL_ARCHIVE`.
14. Hard-regime gate: `skill_half_life_scheduler_v5` `0.81638 +/- 0.00326` versus `cvar_lifetime_guard` `0.82821 +/- 0.00378`.
15. Mechanism gate: contact-mode ablations beat the full method; fixed-risk and stress gates fail.
