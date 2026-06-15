# Submission Readiness Decision

Decision: KILL_ARCHIVE

Last update: 2026-06-15 09:02:54 +01:00

ICLR main-conference readiness: NO.

Reason: The 2026-06-15 v4 rerun confirms the negative result. The half-life scheduler does not decisively beat conformal risk gating (`0.00248 +/- 0.02721` paired goal-success difference on combined micro-shift), and the minus-per-skill-survival ablation improves over the full mechanism (`0.80456` versus `0.79712` goal success). The paper also still lacks real-robot or high-fidelity simulator validation, deployed-data survival learning, and manual full-paper related-work depth.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with robot or accepted high-fidelity benchmark data, a learned survival model, strong conformal/continual-learning baselines, manual related work, and decisive paired gains.
