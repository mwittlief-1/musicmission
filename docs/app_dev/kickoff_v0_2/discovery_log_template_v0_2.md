# Discovery Log Export v0.2

## Session

- Session ID: {{session_id}}
- Mission ID: {{mission_id}}
- Mission title: {{mission_title}}
- Mission version: {{mission_version}}
- Started at: {{started_at}}
- Exported at: {{exported_at}}
- Reconciliation status: {{reconciliation_status}}

## Mission hypothesis

{{hypothesis}}

## Inflation warning

{{inflation_warning}}

## Device / Music context

- Device: {{device_model}}
- iOS version: {{os_version}}
- App version: {{app_version}}
- Music authorization: {{music_authorization_status}}
- Playback capability: {{playback_capability}}
- Storefront/region: {{storefront}}

## Item reactions

{{#item_results}}
### {{sequence}}. {{artist}} — {{title}}

- Item type: {{item_type}}
- Mission item ID: {{mission_item_id}}
- Resolution status: {{resolution_status}}
- Apple Music catalog ID: {{catalog_id}}
- Playback status: {{playback_status}}
- Reaction: {{reaction_value}}
- Reacted at: {{reacted_at}}
- Note: {{note_text}}
- Error/reason: {{reason_or_error}}

{{/item_results}}

## Session summary

- Items in mission: {{item_count}}
- Items resolved: {{resolved_count}}
- Items played: {{played_count}}
- Items reacted to: {{reaction_count}}

## Reconciliation notes

This export is a discovery log only. It does not update the Atlas automatically.
