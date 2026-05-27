#!/usr/bin/env python3
"""Cartenza Affinity Graph-Wide Output Validator v0.3.1 template."""
import argparse, json, sys
from collections import Counter
CORE_DIMS = ["vocal_performance", "emotion_theme", "sonic_texture", "rhythm_body", "form_container"]
OVERLAY_DIMS = ["social_context", "routing_caution"]
REVIEW_CODES = {"recording_identity_unclear","tag_definition_ambiguous","missing_tag_candidate","social_context_unclear","routing_caution_unclear","over_tagged","under_tagged","duplicate_context_unclear","context_leak_risk","version_ambiguity","schema_boundary_risk"}
def tags_in_bucket(bucket):
    return list((bucket or {}).get("primary", [])) + list((bucket or {}).get("secondary", [])) if isinstance(bucket, dict) else []
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tags', required=True); ap.add_argument('--allowed', required=True); args = ap.parse_args()
    data=json.load(open(args.tags, encoding='utf-8')); allowed_doc=json.load(open(args.allowed, encoding='utf-8'))
    allowed_by_dim=allowed_doc['allowed_tags_by_dimension']; rows=data.get('songs', data if isinstance(data, list) else [])
    errors=[]; tag_counter=Counter(); tag_count_dist=Counter(); song_ids=[]; overlay_count=0; empty_social=0
    for i,row in enumerate(rows):
        sid=row.get('canonical_song_recording_id'); song_ids.append(sid); core=row.get('canonical_song_affinity_tags',{}); overlays=row.get('membership_context_overlays',[])
        for dim in core.keys():
            if dim not in CORE_DIMS: errors.append(f'row {i} {sid}: forbidden core dimension {dim}')
        for dim in CORE_DIMS:
            for tag in tags_in_bucket(core.get(dim,{})):
                if tag not in allowed_by_dim.get(dim,[]): errors.append(f'row {i} {sid}: noncanonical/misplaced core tag {tag} in {dim}')
                tag_counter[tag]+=1
        total_core=sum(len(tags_in_bucket(core.get(dim,{}))) for dim in CORE_DIMS); tag_count_dist[total_core]+=1
        if total_core>8:
            codes=set(row.get('review',{}).get('review_reason_codes',[]))
            if 'over_tagged' not in codes and not row.get('tagging_notes'): errors.append(f'row {i} {sid}: >8 core tags without justification')
        for j,ov in enumerate(overlays):
            overlay_count+=1
            for dim in ov.keys():
                if dim in CORE_DIMS: errors.append(f'row {i} {sid} overlay {j}: forbidden overlay core dimension {dim}')
            if not tags_in_bucket(ov.get('social_context',{})): empty_social+=1
            for dim in OVERLAY_DIMS:
                for tag in tags_in_bucket(ov.get(dim,{})):
                    if tag not in allowed_by_dim.get(dim,[]): errors.append(f'row {i} {sid} overlay {j}: noncanonical/misplaced overlay tag {tag} in {dim}')
                    tag_counter[tag]+=1
        for code in row.get('review',{}).get('review_reason_codes',[]):
            if code not in REVIEW_CODES: errors.append(f'row {i} {sid}: unknown review code {code}')
    duplicate_rows=len(song_ids)-len(set(song_ids))
    if duplicate_rows: errors.append(f'duplicate song row count: {duplicate_rows}')
    metrics={'song_rows':len(rows),'membership_overlays':overlay_count,'schema_error_count':len(errors),'duplicate_song_row_count':duplicate_rows,'tag_count_distribution':dict(sorted(tag_count_dist.items())),'safe_gateway_count':tag_counter.get('safe_gateway',0),'context_dependent_count':tag_counter.get('context_dependent',0),'empty_social_context_overlay_count':empty_social,'top_tags':tag_counter.most_common(25)}
    print(json.dumps({'metrics':metrics,'errors':errors[:200]}, indent=2))
    return 1 if errors else 0
if __name__ == '__main__': sys.exit(main())
