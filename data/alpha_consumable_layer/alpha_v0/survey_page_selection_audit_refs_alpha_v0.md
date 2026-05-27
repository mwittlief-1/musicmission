# Survey Page Selection Audit Refs Alpha v0

Alpha contract version: `alpha_v0`

Generated: 2026-05-25T12:50:20.284Z

Status: `ready_for_live_smoke_page_selection_audit`

Purpose: stable Canonical refs/diagnostic labels for Survey/Core page-selection audit without exposing raw graph rows or hidden simulator truth.

## Summary

| metric | count |
| --- | ---: |
| total audit refs | 4228 |
| caution-flagged refs | 826 |

## By Object Type

| object_type | count |
| --- | ---: |
| artist | 1464 |
| album | 1190 |
| song_recording | 1574 |

## By Surface Bucket

| bucket | count |
| --- | ---: |
| page1_core | 576 |
| page2_adaptive | 2224 |
| page3_deep | 1428 |

## Usage Rule

Core/Survey may attach `audit_ref_id`, `candidate_id`, `canonical_entity_ref`, `approved_surface_ref`, `candidate_basis`, family/archetype diagnostic refs, caution flags, and provenance summary to diagnostic artifacts.

These refs are for PM/debug audit, not normal tester UI copy. They are graph references only and do not create user taste or Atlas role truth.
