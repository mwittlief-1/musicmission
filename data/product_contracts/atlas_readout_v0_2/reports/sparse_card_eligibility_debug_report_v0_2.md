# Sparse-Card Eligibility Debug Report v0.2

Source fixture: `fixtures/atlas_home_what_were_seeing_so_far_fixture_v0_2.json`

## Eligibility Rule

A sparse signal may surface when it has at least two positive examples, no negative examples, no meaningful ok/fine drag, coherent graph shape, and useful future testing value.

## Candidate Decisions

| Candidate | Positive examples | Negative examples | Neutral examples | Coherent | Future test value | Eligible | Decision |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| classic/heavy rock | 3 | 0 | 0 | yes | yes | yes | surface |
| older alternative and post-punk | 3 | 0 | 1 | yes | yes | no | surface as secondary branch |
| theatrical/literary indie caution | 0 | 1 | 0 | yes | no | no | do not surface as sparse-clean |

## Surfaced Sparse Card

Title: Small but clean heavy-rock signal

Body: A few body-and-scale rock examples are landing cleanly, without enough volume to call this a center. The pocket is too coherent to ignore, so it needs more evidence.

Evidence: Led Zeppelin, The Who, Black Sabbath

## Notes

Classic/heavy rock qualifies because the fixture has three positive examples, no negative examples, no neutral examples, coherent shape, and useful future testing value. It is deliberately framed as small and unresolved, not as a major region.

Older alternative and post-punk is important but not sparse-clean in this fixture because one neutral/context signal is present. It is rendered as a secondary branch instead.

The theatrical/literary indie caution is not eligible because negative evidence exists. The copy treats that evidence cautiously rather than as permanent exclusion.
