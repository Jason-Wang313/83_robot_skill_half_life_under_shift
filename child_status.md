# Child Status 83

Current stage: ICLR main v5 expanded audit terminal
Last update: 2026-06-21
PDF: C:/Users/wangz/Downloads/83.pdf
PDF pages: 62
PDF SHA256: 33F4831CA807F4D47A799726E3E34CAE97CBEBD7DBFB63EC096965A663524628
GitHub: https://github.com/Jason-Wang313/83_robot_skill_half_life_under_shift
Submission-hardening version: v5 expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the frozen v5 protocol regenerated 307,200 main rollouts, 25,600 physical-state rows, 64,000 ablation rollouts, 392,000 stress rollouts, 96,000 fixed-risk rollouts, and 24 negative cases. On the hard-regime aggregate, `skill_half_life_scheduler_v5` reaches `0.81638 +/- 0.00326` goal success, while `cvar_lifetime_guard` reaches `0.82821 +/- 0.00378`. The paired lower95 versus `cvar_lifetime_guard` is `-0.01528`, and the margin, paired, ablation, fixed-risk, and stress gates fail. No robot hardware or recognized high-fidelity simulator validation is available.
