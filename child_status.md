# Child Status 83

Current stage: ICLR main v4 evidence audit terminal
Last update: 2026-06-15 09:02:54 +01:00
PDF: C:/Users/wangz/Downloads/83.pdf
GitHub: https://github.com/Jason-Wang313/83_robot_skill_half_life_under_shift
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the 2026-06-15 full rerun regenerated 80,640 main rollouts, 14,112 ablation rollouts, and 201,600 stress rollouts. The skill half-life scheduler remains statistically indistinguishable from conformal risk gating on combined micro-shift (`0.00248 +/- 0.02721` paired goal-success difference), and the minus-per-skill-survival ablation still improves over the full mechanism. No robot hardware or high-fidelity simulator validation is available.
