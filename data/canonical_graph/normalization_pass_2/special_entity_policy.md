# Special Entity Policy v0.2

Generated: 2026-05-20

Minimal supported entity classes:

`composition`, `musical_work`, `show`, `film`, `score_album`, `curated_soundtrack`, `cast_recording`, `fictional_performer`, `church_brand`, `worship_standard`, `traditional_song`, `use_case_context_object`, `channel_object`, `compilation_album`, `live_album`, `ep`, `mixtape`.

Every special entity row declares `survey_safe`, `reaction_target_type`, `apple_music_resolution_policy`, `atlas_promotion_policy`, and `do_not_infer_rules`.

Rows are allowed to remain in canonical source data while being blocked from Fast Survey and default mission generation through `canonical_quarantine_queue.json`.
