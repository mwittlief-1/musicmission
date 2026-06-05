declare const Deno: {
  serve(handler: (request: Request) => Response | Promise<Response>): void;
  env: { get(key: string): string | undefined };
};

type JsonObject = Record<string, unknown>;

type MissionItem = {
  item_id?: string;
  sequence?: number;
  item_type?: string;
  artist?: string;
  title?: string;
  album?: string | null;
  year?: number | null;
  alpha_route_role?: string | null;
  alpha_source_mission_type?: string | null;
  alpha_target_object_ids?: string[] | null;
  alpha_graph_context_refs?: string[] | null;
};

type Mission = {
  mission_id?: string;
  mission_title?: string;
  mission_type?: string;
  hypothesis?: string;
  brief?: string | null;
  why_this_mission_now?: string | null;
  alpha_mission_archetype?: string | null;
  source_trace_summary?: string | null;
  items?: MissionItem[];
};

type EnrichmentRequest = {
  client_request_id?: string;
  tester_alias?: string;
  mission_index?: number;
  mission_total?: number;
  source_app_version?: string;
  source_app_build?: string;
  replay_enrichment_output?: JsonObject;
  mission?: Mission;
};

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const tagRegistry: Record<string, { display_label: string; valid_primary_reactions: string[]; atlas_effect: string }> = {
  HOOK_WORKED: { display_label: "The hook worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_songcraft_signal" },
  MELODY_WORKED: { display_label: "The melody worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_melody_signal" },
  GROOVE_WORKED: { display_label: "The groove worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_rhythm_body_signal" },
  BEAT_WORKED: { display_label: "The beat worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_beat_or_rhythm_signal" },
  VOICE_WORKED: { display_label: "The voice worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_vocal_signal" },
  PERFORMANCE_WORKED: { display_label: "The performance worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_performance_signal" },
  LYRICS_WORKED: { display_label: "The words worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_lyric_or_story_signal" },
  MOOD_WORKED: { display_label: "The mood worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_mood_signal" },
  ENERGY_WORKED: { display_label: "The energy worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_energy_signal" },
  SOUND_WORKED: { display_label: "The sound worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_sound_or_texture_signal" },
  PRODUCTION_WORKED: { display_label: "The production worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_production_signal" },
  ARRANGEMENT_WORKED: { display_label: "The arrangement worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_arrangement_signal" },
  STORY_WORKED: { display_label: "The story worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_story_or_theme_signal" },
  BUILD_WORKED: { display_label: "The build worked", valid_primary_reactions: ["love", "like"], atlas_effect: "strengthen_dynamic_shape_signal" },
  SURPRISED_ME: { display_label: "This surprised me", valid_primary_reactions: ["love", "like", "ok"], atlas_effect: "open_or_strengthen_novelty_signal" },
  WOULD_TRY_MORE_NEARBY: { display_label: "I'd try more nearby", valid_primary_reactions: ["love", "like", "ok"], atlas_effect: "open_nearby_exploration" },
  GOOD_NOT_CORE: { display_label: "Good, not core", valid_primary_reactions: ["like", "ok"], atlas_effect: "mark_waypoint_not_landmark" },
  GOOD_NOT_FOR_ME: { display_label: "Good, not for me", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_respect_without_appetite" },
  RIGHT_SOUND_WRONG_SONG: { display_label: "Right sound, wrong song", valid_primary_reactions: ["like", "ok", "dislike"], atlas_effect: "split_affinity_from_song_object" },
  RIGHT_ARTIST_WRONG_TRACK: { display_label: "Right artist, wrong track", valid_primary_reactions: ["like", "ok", "dislike"], atlas_effect: "split_artist_from_song_object" },
  TOO_FAMILIAR: { display_label: "Too familiar", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_familiarity_drag" },
  TOO_PREDICTABLE: { display_label: "Too predictable", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_predictability_drag" },
  TOO_BUSY: { display_label: "Too busy", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_density_drag" },
  TOO_FLAT: { display_label: "Too flat", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_dynamic_drag" },
  WRONG_MOOD: { display_label: "Wrong mood", valid_primary_reactions: ["ok", "dislike"], atlas_effect: "mark_contextual_mood_mismatch" },
  LOST_ME_FAST: { display_label: "Lost me fast", valid_primary_reactions: ["dislike"], atlas_effect: "strengthen_fast_rejection_boundary" },
};

const allowedTagIDs = Object.keys(tagRegistry);

const missionEnrichmentOutputSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "schema_version",
    "mission_id",
    "mission_copy",
    "route_item_copy",
    "secondary_reaction_tag_candidates",
    "post_completion_interpretation_seeds",
    "internal_quality_notes",
  ],
  properties: {
    schema_version: { type: "string", const: "mission_enrichment_output_v0_2" },
    mission_id: { type: "string", minLength: 1 },
    mission_copy: {
      type: "object",
      additionalProperties: false,
      required: ["title", "subtitle", "short_description", "why_now", "listen_for", "mission_hypothesis_user_facing"],
      properties: {
        title: { type: "string", minLength: 1, maxLength: 80 },
        subtitle: { type: "string", minLength: 1, maxLength: 160 },
        short_description: { type: "string", minLength: 1, maxLength: 420 },
        why_now: { type: "string", minLength: 1, maxLength: 320 },
        listen_for: { type: "array", minItems: 2, maxItems: 4, items: { type: "string", minLength: 1, maxLength: 160 } },
        mission_hypothesis_user_facing: { type: "string", minLength: 1, maxLength: 320 },
      },
    },
    route_item_copy: {
      type: "array",
      minItems: 1,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["item_id", "pre_play_line", "why_this_song", "listen_for"],
        properties: {
          item_id: { type: "string", minLength: 1 },
          pre_play_line: { type: "string", minLength: 1, maxLength: 180 },
          why_this_song: { type: "string", minLength: 1, maxLength: 260 },
          listen_for: { type: "array", minItems: 1, maxItems: 3, items: { type: "string", minLength: 1, maxLength: 160 } },
        },
      },
    },
    secondary_reaction_tag_candidates: {
      type: "array",
      minItems: 1,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["item_id", "tags"],
        properties: {
          item_id: { type: "string", minLength: 1 },
          tags: {
            type: "array",
            minItems: 1,
            maxItems: 6,
            items: {
              type: "object",
              additionalProperties: false,
              required: [
                "tag_id",
                "rank",
                "display_label",
                "valid_primary_reactions",
                "why_this_tag_is_relevant",
                "linked_song_affinity_tags",
                "linked_user_alignment_hints",
                "atlas_effect",
                "atlas_signal_target",
              ],
              properties: {
                tag_id: { type: "string", enum: allowedTagIDs },
                rank: { type: "integer", minimum: 1, maximum: 6 },
                display_label: { type: "string", minLength: 1 },
                valid_primary_reactions: {
                  type: "array",
                  minItems: 1,
                  items: { type: "string", enum: ["love", "like", "ok", "dislike"] },
                },
                why_this_tag_is_relevant: { type: "string", minLength: 1, maxLength: 360 },
                linked_song_affinity_tags: { type: "array", items: { type: "string" } },
                linked_user_alignment_hints: { type: "array", items: { type: "string" } },
                atlas_effect: { type: "string", minLength: 1 },
                atlas_signal_target: {
                  type: "object",
                  additionalProperties: false,
                  required: ["target_type", "target_labels"],
                  properties: {
                    target_type: { type: "string", enum: ["affinity_tag", "pattern", "region", "mission_hypothesis", "boundary", "frontier", "context_rule"] },
                    target_labels: { type: "array", items: { type: "string", minLength: 1 } },
                  },
                },
              },
            },
          },
        },
      },
    },
    post_completion_interpretation_seeds: {
      type: "array",
      minItems: 3,
      items: {
        type: "object",
        additionalProperties: false,
        required: ["condition", "readout_seed", "atlas_inference_hint"],
        properties: {
          condition: { type: "string", enum: ["mostly_positive", "mixed", "mostly_negative"] },
          readout_seed: { type: "string", minLength: 1, maxLength: 320 },
          atlas_inference_hint: { type: "string", minLength: 1, maxLength: 320 },
        },
      },
    },
    internal_quality_notes: {
      type: "object",
      additionalProperties: false,
      required: ["used_song_affinity_tags", "used_alignment_hints", "avoided_overclaims", "risk_flags"],
      properties: {
        used_song_affinity_tags: { type: "array", items: { type: "string" } },
        used_alignment_hints: { type: "array", items: { type: "string" } },
        avoided_overclaims: { type: "array", items: { type: "string" } },
        risk_flags: { type: "array", items: { type: "string" } },
      },
    },
  },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

function env(name: string): string | undefined {
  return Deno.env.get(`CARTENZA_${name}`) ?? Deno.env.get(`WAYMARK_${name}`) ?? Deno.env.get(name);
}

function compactMission(mission: Mission): JsonObject {
  return {
    mission_id: mission.mission_id,
    mission_title: mission.mission_title,
    mission_type: mission.mission_type,
    hypothesis: mission.hypothesis,
    brief: mission.brief,
    why_this_mission_now: mission.why_this_mission_now,
    alpha_mission_archetype: mission.alpha_mission_archetype,
    source_trace_summary: mission.source_trace_summary,
    route_items: (mission.items ?? []).map((item) => ({
      item_id: item.item_id,
      sequence: item.sequence,
      item_type: item.item_type,
      artist: item.artist,
      title: item.title,
      album: item.album,
      year: item.year,
      route_role: item.alpha_route_role,
      source_mission_type: item.alpha_source_mission_type,
      target_object_ids: item.alpha_target_object_ids ?? [],
      graph_context_refs: item.alpha_graph_context_refs ?? [],
      allowed_secondary_reaction_tag_ids: allowedTagIDs,
    })),
  };
}

function buildPrompt(request: EnrichmentRequest): string {
  return [
    "You are enriching a deterministic Cartenza listening mission for app display.",
    "",
    "Write concise, user-facing mission copy, route-item setup copy, and secondary reaction tag candidates.",
    "",
    "Rules:",
    "- Do not change the mission, songs, order, route roles, IDs, or canonical identities.",
    "- Do not invent artists, songs, genres, user history, or final taste truth.",
    "- Use only allowed secondary reaction tag IDs.",
    "- display_label must exactly match the approved registry label.",
    "- Treat user context as provisional and use words like test, explore, check, clarify, and refine.",
    "- Do not expose raw graph IDs or schema labels in display copy.",
    "- Return valid JSON only matching mission_enrichment_output_v0_2.",
    "",
    "Required output shape:",
    JSON.stringify({
      schema_version: "mission_enrichment_output_v0_2",
      mission_id: "same mission_id",
      mission_copy: {
        title: "max 80 chars",
        subtitle: "max 160 chars",
        short_description: "max 420 chars",
        why_now: "max 320 chars",
        listen_for: ["2-4 short phrases"],
        mission_hypothesis_user_facing: "max 320 chars",
      },
      route_item_copy: [
        { item_id: "same item_id", pre_play_line: "max 180 chars", why_this_song: "max 260 chars", listen_for: ["1-3 phrases"] },
      ],
      secondary_reaction_tag_candidates: [
        {
          item_id: "same item_id",
          tags: [
            {
              tag_id: "APPROVED_TAG_ID",
              rank: 1,
              display_label: "exact registry label",
              valid_primary_reactions: ["love"],
              why_this_tag_is_relevant: "max 360 chars",
              linked_song_affinity_tags: [],
              linked_user_alignment_hints: [],
              atlas_effect: "registry atlas_effect",
              atlas_signal_target: { target_type: "mission_hypothesis", target_labels: ["display-safe phrase"] },
            },
          ],
        },
      ],
      post_completion_interpretation_seeds: [
        { condition: "mostly_positive", readout_seed: "text", atlas_inference_hint: "text" },
        { condition: "mixed", readout_seed: "text", atlas_inference_hint: "text" },
        { condition: "mostly_negative", readout_seed: "text", atlas_inference_hint: "text" },
      ],
      internal_quality_notes: {
        used_song_affinity_tags: [],
        used_alignment_hints: [],
        avoided_overclaims: [],
        risk_flags: [],
      },
    }),
    "",
    "Approved secondary reaction tag registry:",
    JSON.stringify(tagRegistry),
    "",
    "Mission payload:",
    JSON.stringify(compactMission(request.mission ?? {})),
  ].join("\n");
}

async function callOpenAI(request: EnrichmentRequest): Promise<{ output: JsonObject; model: string; usage: unknown; latency_ms: number }> {
  const apiKey = env("OPENAI_API_KEY");
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured for mission enrichment.");
  }

  const model = env("OPENAI_ENRICHMENT_MODEL") ?? env("OPENAI_MODEL") ?? "gpt-4.1";
  const started = Date.now();
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      input: [
        {
          role: "user",
          content: [{ type: "input_text", text: buildPrompt(request) }],
        },
      ],
      text: {
        format: {
          type: "json_schema",
          name: "mission_enrichment_output_v0_2",
          strict: true,
          schema: missionEnrichmentOutputSchema,
        },
      },
      max_output_tokens: 7000,
      store: false,
    }),
  });

  const raw = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`OpenAI enrichment failed with HTTP ${response.status}: ${JSON.stringify(raw).slice(0, 800)}`);
  }

  const outputText = extractOutputText(raw);
  return {
    output: JSON.parse(outputText) as JsonObject,
    model,
    usage: (raw as JsonObject).usage ?? null,
    latency_ms: Date.now() - started,
  };
}

function extractOutputText(raw: unknown): string {
  const output = (raw as JsonObject).output;
  if (Array.isArray(output)) {
    const textParts: string[] = [];
    for (const item of output) {
      const content = (item as JsonObject).content;
      if (!Array.isArray(content)) continue;
      for (const contentItem of content) {
        const text = (contentItem as JsonObject).text;
        if (typeof text === "string") textParts.push(text);
      }
    }
    if (textParts.length > 0) return textParts.join("\n");
  }

  const outputText = (raw as JsonObject).output_text;
  if (typeof outputText === "string") return outputText;
  throw new Error("OpenAI response did not include output text.");
}

function validateEnrichment(output: JsonObject, mission: Mission): string[] {
  const errors: string[] = [];
  const missionID = mission.mission_id;
  const itemIDs = (mission.items ?? []).map((item) => item.item_id).filter((id): id is string => typeof id === "string");

  if (output.schema_version !== "mission_enrichment_output_v0_2") errors.push("schema_version must be mission_enrichment_output_v0_2.");
  if (output.mission_id !== missionID) errors.push("mission_id must match the deterministic mission.");

  const routeItems = output.route_item_copy;
  const tagSets = output.secondary_reaction_tag_candidates;
  if (!Array.isArray(routeItems) || routeItems.length !== itemIDs.length) errors.push("route_item_copy must include every route item once.");
  if (!Array.isArray(tagSets) || tagSets.length !== itemIDs.length) errors.push("secondary_reaction_tag_candidates must include every route item once.");

  const routeIDs = new Set(Array.isArray(routeItems) ? routeItems.map((item) => (item as JsonObject).item_id) : []);
  const tagIDs = new Set(Array.isArray(tagSets) ? tagSets.map((item) => (item as JsonObject).item_id) : []);
  for (const itemID of itemIDs) {
    if (!routeIDs.has(itemID)) errors.push(`route_item_copy missing ${itemID}.`);
    if (!tagIDs.has(itemID)) errors.push(`secondary_reaction_tag_candidates missing ${itemID}.`);
  }

  if (Array.isArray(tagSets)) {
    for (const tagSet of tagSets as JsonObject[]) {
      const tags = tagSet.tags;
      if (!Array.isArray(tags) || tags.length === 0) {
        errors.push(`${String(tagSet.item_id)} must include tags.`);
        continue;
      }
      const covered = new Set<string>();
      for (const tag of tags as JsonObject[]) {
        const tagID = tag.tag_id;
        const registryEntry = typeof tagID === "string" ? tagRegistry[tagID] : undefined;
        if (!registryEntry) {
          errors.push(`Unsupported tag_id ${String(tagID)}.`);
          continue;
        }
        if (tag.display_label !== registryEntry.display_label) {
          errors.push(`${tagID} display_label must match registry.`);
        }
        const reactions = tag.valid_primary_reactions;
        if (!Array.isArray(reactions) || reactions.length === 0) {
          errors.push(`${tagID} must include valid_primary_reactions.`);
          continue;
        }
        for (const reaction of reactions) {
          if (typeof reaction !== "string" || !registryEntry.valid_primary_reactions.includes(reaction)) {
            errors.push(`${tagID} has invalid primary reaction ${String(reaction)}.`);
          } else {
            covered.add(reaction);
          }
        }
      }
      for (const required of ["love", "like", "ok", "dislike"]) {
        if (!covered.has(required)) errors.push(`${String(tagSet.item_id)} is missing a ${required} secondary tag.`);
      }
    }
  }

  return errors;
}

Deno.serve(async (request: Request) => {
  if (request.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (request.method !== "POST") return jsonResponse({ error: "Method not allowed" }, 405);

  try {
    const payload = (await request.json()) as EnrichmentRequest;
    if (!payload.mission?.mission_id || !Array.isArray(payload.mission.items) || payload.mission.items.length === 0) {
      return jsonResponse({ error: "mission with route items is required" }, 400);
    }

    const started = Date.now();
    const openAIResult = payload.replay_enrichment_output
      ? { output: payload.replay_enrichment_output, model: "replay", usage: null, latency_ms: 0 }
      : await callOpenAI(payload);
    const validationErrors = validateEnrichment(openAIResult.output, payload.mission);
    if (validationErrors.length > 0) {
      return jsonResponse({ status: "blocked", mission_id: payload.mission.mission_id, validation_errors: validationErrors }, 422);
    }

    return jsonResponse({
      schema_version: "cartenza.mission_enrichment_runtime_response.v0.1",
      status: "enriched",
      mission_id: payload.mission.mission_id,
      model: openAIResult.model,
      latency_ms: Date.now() - started,
      usage: openAIResult.usage,
      enrichment_output: openAIResult.output,
    });
  } catch (error) {
    return jsonResponse({ status: "error", error: error instanceof Error ? error.message : String(error) }, 500);
  }
});
