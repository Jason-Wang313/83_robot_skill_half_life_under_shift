# Submission Readiness Decision

Decision: KILL_ARCHIVE

Last update: 2026-06-21

ICLR main-conference readiness: NO.

Reason: The frozen v5 expanded audit confirms the negative result at larger scale. `skill_half_life_scheduler_v5` reaches `0.81638 +/- 0.00326` hard-regime goal success, while the strongest non-oracle baseline, `cvar_lifetime_guard`, reaches `0.82821 +/- 0.00378`. The paired hard-aggregate lower95 versus `cvar_lifetime_guard` is `-0.01528`. The method also fails the ablation, fixed-risk, and maximum-stress gates.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with robot hardware or accepted high-fidelity benchmark data, a learned survival model trained on deployment traces, stronger external baselines, manual expert related-work vetting, fixed-risk coverage that does not collapse, and decisive paired gains.
