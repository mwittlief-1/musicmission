# Physical Device MusicKit QA Checklist

Purpose: verify that trusted Alpha evidence comes from a real iPhone using live MusicKit behavior, not simulator or stub playback.

## Setup

- Build configuration: Release or TestFlight-equivalent signed build.
- Device: physical iPhone, trusted on the Mac if running locally.
- Apple Music: signed in, MusicKit authorization granted, subscription active.
- Mission source: reviewed assignment/import only, not bundled mission library.

## Playback Loop

- Launch with no bundled user mission content.
- Import or receive one reviewed mission assignment.
- Resolve the first route item through live MusicKit search.
- Start playback and confirm audio begins on the iPhone.
- Pause, resume, and stop from the player surface.
- Seek forward and backward with the progress control.
- Use next/skip after playback has started and confirm the item records skipped/no-signal rather than dislike.
- Let a track complete and confirm auto-advance starts the next playable item.
- Relaunch the app and confirm mission, selected item, reactions, notes, and playback evidence restore.

## Resolution / Failure Cases

- Confirm top-result resolution records catalog ID, catalog URL, storefront, candidate count, confidence, resolver, and resolved metadata.
- Mark or observe unavailable-region behavior if a track cannot play.
- Mark or observe unavailable-subscription behavior if account playback is blocked.
- Confirm wrong/ambiguous resolution can be surfaced for Mission Review instead of being silently accepted.

## Evidence / Export

- Record at least one primary reaction.
- Select at least one contextual chip.
- Add an optional typed or dictated note.
- Generate and save an acceptance export only on the physical iPhone.
- Confirm `device_context.is_physical_device = true`.
- Confirm `atlas_signal_candidate_bundle.writes_atlas_truth = false`.
- Confirm skipped/no-signal evidence appears as review-needed candidate evidence, not an automatic negative.

## Pass / Fail Notes

- Pass requires live playback, evidence capture, relaunch restore, and saved export.
- Simulator or stub exports may validate contracts but do not count as physical-device acceptance evidence.
