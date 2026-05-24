declare const Deno: {
  serve(handler: (request: Request) => Response | Promise<Response>): void;
  env: { get(key: string): string | undefined };
};

type JsonObject = Record<string, unknown>;

type AlphaGenerationRequest = {
  client_request_id?: string;
  tester_alias?: string;
  requested_batch_size?: number;
  survey_evidence_export?: JsonObject;
  mission_generation_digest_view?: JsonObject;
  candidate_pool?: JsonObject;
  prompt_context?: JsonObject;
  replay_generation_output?: JsonObject;
};

type ValidationResult = {
  valid: boolean;
  errors: string[];
};

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const missionOutputSchemaVersion =
  Deno.env.get("WAYMARK_MISSION_OUTPUT_SCHEMA_VERSION") ?? "waymark.mission_output.v0.1";
const appMissionSchemaVersion =
  Deno.env.get("WAYMARK_APP_MISSION_SCHEMA_VERSION") ?? "mission.v0.2";
const adapterVersion =
  Deno.env.get("WAYMARK_APP_MISSION_ADAPTER_VERSION") ?? "supabase_generate_first_mission_batch_adapter_v0_1";

const missionOutputSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "schema_version",
    "mission_id",
    "source_prompt",
    "title",
    "archetypes",
    "brief",
    "hypothesis",
    "why_now",
    "risk_model",
    "route",
    "completion_criteria",
    "review_config",
    "completion_summary_inputs",
    "possible_atlas_update_candidates",
  ],
  properties: {
    schema_version: { type: "string", const: missionOutputSchemaVersion },
    mission_id: { type: "string", minLength: 1 },
    source_prompt: { type: "string", minLength: 1 },
    title: { type: "string", minLength: 1 },
    archetypes: { type: "array", items: { type: "string" } },
    brief: { type: "string", minLength: 1 },
    hypothesis: { type: "string", minLength: 1 },
    why_now: { type: "string", minLength: 1 },
    risk_model: {
      type: "object",
      additionalProperties: false,
      required: ["overall_risk", "known_traps_acknowledged", "uncertainty_notes", "candidate_policy"],
      properties: {
        overall_risk: { type: "string", enum: ["low", "medium", "high"] },
        known_traps_acknowledged: { type: "array", items: { type: "string" } },
        uncertainty_notes: { type: "array", items: { type: "string" } },
        candidate_policy: { type: "string" },
      },
    },
    route: {
      type: "object",
      additionalProperties: false,
      required: ["route_summary", "intended_item_count", "items"],
      properties: {
        route_summary: { type: "string", minLength: 1 },
        intended_item_count: { type: "integer", minimum: 1 },
        items: {
          type: "array",
          minItems: 1,
          items: {
            type: "object",
            additionalProperties: false,
            required: [
              "route_index",
              "item_id",
              "candidate_id",
              "item_type",
              "display_metadata",
              "selection_role",
              "risk_class",
              "familiarity_assumption",
              "why_selected",
              "route_function",
              "item_hypothesis",
              "expected_positive_signal",
              "expected_negative_signal",
              "expected_features",
              "feedback_chip_sets",
              "music_kit_search_hint",
              "review_state",
            ],
            properties: {
              route_index: { type: "integer", minimum: 1 },
              item_id: { type: "string", minLength: 1 },
              candidate_id: { type: "string" },
              item_type: { type: "string", enum: ["track", "album"] },
              display_metadata: {
                type: "object",
                additionalProperties: false,
                required: ["artist", "title", "album", "release_year"],
                properties: {
                  artist: { type: "string", minLength: 1 },
                  title: { type: "string", minLength: 1 },
                  album: { type: "string" },
                  release_year: { type: "integer", minimum: 1900, maximum: 2100 },
                },
              },
              selection_role: {
                type: "string",
                enum: ["anchor", "bridge", "probe", "trap", "checkpoint", "cooldown"],
              },
              risk_class: { type: "string", enum: ["safe", "medium", "risky", "trap", "dead_end_check"] },
              familiarity_assumption: {
                type: "string",
                enum: ["deeply_known", "familiar", "title_known", "unknown"],
              },
              why_selected: { type: "string", minLength: 1 },
              route_function: { type: "string", minLength: 1 },
              item_hypothesis: { type: "string", minLength: 1 },
              expected_positive_signal: { type: "string", minLength: 1 },
              expected_negative_signal: { type: "string", minLength: 1 },
              expected_features: { type: "array", items: { type: "string" } },
              feedback_chip_sets: {
                type: "object",
                additionalProperties: false,
                required: ["love", "like", "keep", "not_for_me"],
                properties: {
                  love: { type: "array", minItems: 2, items: { $ref: "#/$defs/feedback_chip" } },
                  like: { type: "array", minItems: 2, items: { $ref: "#/$defs/feedback_chip" } },
                  keep: { type: "array", minItems: 2, items: { $ref: "#/$defs/feedback_chip" } },
                  not_for_me: { type: "array", minItems: 2, items: { $ref: "#/$defs/feedback_chip" } },
                },
              },
              music_kit_search_hint: {
                type: "object",
                additionalProperties: false,
                required: [
                  "search_query",
                  "artist",
                  "title",
                  "album",
                  "preferred_version_notes",
                  "avoid_versions",
                  "resolution_status_placeholder",
                ],
                properties: {
                  search_query: { type: "string", minLength: 1 },
                  artist: { type: "string", minLength: 1 },
                  title: { type: "string", minLength: 1 },
                  album: { type: "string" },
                  preferred_version_notes: { type: "string" },
                  avoid_versions: { type: "string" },
                  resolution_status_placeholder: {
                    type: "string",
                    enum: ["unresolved", "ambiguous", "unavailable_region"],
                  },
                },
              },
              review_state: {
                type: "object",
                additionalProperties: false,
                required: ["needs_human_review", "review_notes", "uncertainty_flags"],
                properties: {
                  needs_human_review: { type: "boolean" },
                  review_notes: { type: "string" },
                  uncertainty_flags: { type: "array", items: { type: "string" } },
                },
              },
            },
          },
        },
      },
    },
    completion_criteria: {
      type: "object",
      additionalProperties: false,
      required: [
        "min_items_to_play",
        "min_primary_reactions",
        "primary_reaction_policy",
        "min_chip_selections_for_summary",
        "chip_selection_policy",
        "completion_logic",
      ],
      properties: {
        min_items_to_play: { type: "integer", minimum: 1 },
        min_primary_reactions: { type: "integer", minimum: 1 },
        primary_reaction_policy: { type: "string" },
        min_chip_selections_for_summary: { type: "integer", minimum: 0 },
        chip_selection_policy: { type: "string" },
        completion_logic: { type: "string" },
      },
    },
    review_config: {
      type: "object",
      additionalProperties: false,
      required: [
        "requires_human_review",
        "ready_for_app_import",
        "default_item_review_needed_for",
        "frontier_or_trap_review_policy",
        "review_focus",
        "notes",
      ],
      properties: {
        requires_human_review: { type: "boolean" },
        ready_for_app_import: { type: "boolean" },
        default_item_review_needed_for: { type: "array", items: { type: "string" } },
        frontier_or_trap_review_policy: { type: "string" },
        review_focus: { type: "array", items: { type: "string" } },
        notes: { type: "string" },
      },
    },
    completion_summary_inputs: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["input_id", "prompt", "source"],
        properties: {
          input_id: { type: "string" },
          prompt: { type: "string" },
          source: { type: "string" },
        },
      },
    },
    possible_atlas_update_candidates: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["candidate_id", "trigger_conditions", "atlas_role", "confidence", "rationale", "review_required"],
        properties: {
          candidate_id: { type: "string" },
          trigger_conditions: {
            type: "array",
            items: {
              type: "object",
              additionalProperties: false,
              required: [
                "condition_id",
                "future_reaction_operations",
                "required_signal",
                "minimum_occurrences",
                "condition_text",
              ],
              properties: {
                condition_id: { type: "string" },
                future_reaction_operations: {
                  type: "array",
                  items: { type: "string", enum: ["love", "like", "keep", "not_for_me"] },
                },
                required_signal: { type: "string" },
                minimum_occurrences: { type: "integer", minimum: 1 },
                condition_text: { type: "string" },
              },
            },
          },
          atlas_role: {
            type: "string",
            enum: ["Landmark", "Region", "Frontier", "Dead End", "Waypoint", "Signal only"],
          },
          confidence: { type: "string", enum: ["low", "medium", "high"] },
          rationale: { type: "string" },
          review_required: { type: "boolean" },
        },
      },
    },
  },
  $defs: {
    feedback_chip: {
      type: "object",
      additionalProperties: false,
      required: [
        "chip_id",
        "label",
        "reaction_operation",
        "chip_type",
        "signal_meaning",
        "mapped_canonical_feature_id",
        "atlas_effect_hint",
        "weight_hint",
        "uses_user_vocabulary",
      ],
      properties: {
        chip_id: { type: "string", minLength: 1 },
        label: { type: "string", minLength: 1 },
        reaction_operation: { type: "string", enum: ["love", "like", "keep", "not_for_me"] },
        chip_type: { type: "string" },
        signal_meaning: { type: "string" },
        mapped_canonical_feature_id: { type: "string" },
        atlas_effect_hint: { type: "string" },
        weight_hint: { type: "string", enum: ["low", "medium", "high", "negative"] },
        uses_user_vocabulary: { type: "boolean" },
      },
    },
  },
} as const;

Deno.serve(async (request: Request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return jsonResponse({ error: "method_not_allowed" }, 405);
  }

  const startedAt = performance.now();
  const runId = crypto.randomUUID();
  const promptVersion = Deno.env.get("WAYMARK_GENERATION_PROMPT_VERSION") ??
    "mission_generator_candidate_constrained_v0_1";
  const model = Deno.env.get("WAYMARK_OPENAI_MODEL") ?? "gpt-5.4-mini";

  let inputPacket: AlphaGenerationRequest;
  try {
    inputPacket = await request.json();
  } catch {
    return jsonResponse({ run_id: runId, error: "invalid_json" }, 400);
  }

  const inputValidation = validateInputPacket(inputPacket);
  if (!inputValidation.valid) {
    return jsonResponse({ run_id: runId, error: "invalid_input", validation: inputValidation }, 400);
  }
  if (inputPacket.replay_generation_output !== undefined && !isReplayModeEnabled()) {
    return jsonResponse({ run_id: runId, error: "replay_mode_disabled" }, 400);
  }

  const inputPacketSha256 = await sha256JSON(inputPacket);

  await createRun(runId, {
    client_request_id: inputPacket.client_request_id,
    tester_alias: inputPacket.tester_alias,
    status: "received",
    app_import_status: "not_checked",
    prompt_version: promptVersion,
    model,
    adapter_version: adapterVersion,
    mission_output_schema_version: missionOutputSchemaVersion,
    app_mission_schema_version: appMissionSchemaVersion,
    input_packet_sha256: inputPacketSha256,
    input_packet: inputPacket,
  });

  try {
    const openAIRequest = buildOpenAIRequest(model, promptVersion, inputPacket);
    await updateRun(runId, {
      status: "generating",
      openai_request: openAIRequest,
    });

    const rawOpenAIResponse = isReplayModeEnabled() && isObject(inputPacket.replay_generation_output)
      ? buildReplayOpenAIResponse(inputPacket.replay_generation_output)
      : await callOpenAI(openAIRequest);
    await updateRun(runId, {
      raw_openai_response: rawOpenAIResponse,
    });

    const generatedText = extractOutputText(rawOpenAIResponse);
    const parsedGeneration = JSON.parse(generatedText) as JsonObject;
    const generationValidation = validateMissionOutput(parsedGeneration);
    const appMissions = generationValidation.valid && isReadyForAppImport(parsedGeneration)
      ? [toAppMission(parsedGeneration)]
      : [];
    const appMissionValidation = appMissions.length > 0
      ? validateAppMission(appMissions[0] as JsonObject)
      : { valid: true, errors: [] };
    const appImportStatus = deriveAppImportStatus(
      generationValidation,
      appMissionValidation,
      parsedGeneration,
    );
    const status = appImportStatus;
    const latencyMs = Math.round(performance.now() - startedAt);
    const usage = extractUsage(rawOpenAIResponse);

    await updateRun(runId, {
      status,
      app_import_status: appImportStatus,
      raw_openai_response: rawOpenAIResponse,
      parsed_generation: parsedGeneration,
      app_missions: appMissions,
      validation: {
        generation: generationValidation,
        app_mission: appMissionValidation,
      },
      token_usage: usage,
      latency_ms: latencyMs,
    });

    return jsonResponse({
      run_id: runId,
      status,
      prompt_version: promptVersion,
      model,
      adapter_version: adapterVersion,
      mission_output_schema_version: missionOutputSchemaVersion,
      app_mission_schema_version: appMissionSchemaVersion,
      input_packet_sha256: inputPacketSha256,
      generation: parsedGeneration,
      app_missions: appImportStatus === "app_import_candidate" ? appMissions : [],
      validation: {
        generation: generationValidation,
        app_mission: appMissionValidation,
      },
      usage,
      latency_ms: latencyMs,
    });
  } catch (error) {
    const latencyMs = Math.round(performance.now() - startedAt);
    const message = error instanceof Error ? error.message : String(error);
    await updateRun(runId, {
      status: "failed",
      app_import_status: "blocked",
      error_message: message,
      latency_ms: latencyMs,
    });
    return jsonResponse({ run_id: runId, status: "failed", error: message }, 500);
  }
});

function validateInputPacket(packet: AlphaGenerationRequest): ValidationResult {
  const errors: string[] = [];
  if (!isObject(packet.survey_evidence_export)) {
    errors.push("survey_evidence_export must be an object");
  }
  if (!isObject(packet.mission_generation_digest_view)) {
    errors.push("mission_generation_digest_view must be an object");
  }
  if (packet.candidate_pool !== undefined && !isObject(packet.candidate_pool)) {
    errors.push("candidate_pool must be an object when supplied");
  }
  if (
    packet.requested_batch_size !== undefined &&
    (!Number.isInteger(packet.requested_batch_size) || packet.requested_batch_size < 1)
  ) {
    errors.push("requested_batch_size must be a positive integer when supplied");
  }
  return { valid: errors.length === 0, errors };
}

function buildOpenAIRequest(model: string, promptVersion: string, packet: AlphaGenerationRequest): JsonObject {
  const maxOutputTokens = parseInt(Deno.env.get("WAYMARK_OPENAI_MAX_OUTPUT_TOKENS") ?? "12000", 10);
  const reasoningEffort = Deno.env.get("WAYMARK_OPENAI_REASONING_EFFORT");
  const systemPrompt = [
    "You generate Waymark trusted Alpha first-batch listening missions.",
    "Use only the supplied Survey evidence, MissionGenerationDigestView, and candidate pool.",
    "If the candidate pool includes mission_intent, mission_request, or mission_portfolio_slot, treat them as controlling context for the mission archetype, route shape, risk model, and objective.",
    "Mission intents are generic Atlas-signal tests. Do not turn fixture examples, known tester taste, or a named artist/country into the mission concept unless that named object is present in the supplied candidate pool and source signal refs.",
    "Do not use songs merely because they appeared in the Survey grid; route items must come from the supplied candidate pool and serve the mission_request.",
    "A mission is a structured listening experiment, not a playlist.",
    "Do not promote provisional evidence into Atlas truth.",
    "Return only JSON matching the provided schema.",
  ].join(" ");

  const userPayload = {
    prompt_version: promptVersion,
    requested_batch_size: packet.requested_batch_size ?? 3,
    survey_evidence_export: packet.survey_evidence_export,
    mission_generation_digest_view: packet.mission_generation_digest_view,
    candidate_pool: packet.candidate_pool ?? {},
    prompt_context: packet.prompt_context ?? {},
    output_contract_notes: {
      app_gate: "Set review_config.ready_for_app_import true only when every route item is concrete and playable via MusicKit search.",
      mission_shape: "Respect candidate_pool.mission_intent, candidate_pool.mission_request, and candidate_pool.mission_portfolio_slot when present.",
      reaction_operations: ["love", "like", "keep", "not_for_me"],
      no_overclaiming: "All possible Atlas updates must stay review-gated.",
    },
  };

  const request: JsonObject = {
    model,
    input: [
      { role: "system", content: [{ type: "input_text", text: systemPrompt }] },
      { role: "user", content: [{ type: "input_text", text: JSON.stringify(userPayload, null, 2) }] },
    ],
    text: {
      format: {
        type: "json_schema",
        name: "waymark_mission_output_v0_1",
        strict: true,
        schema: missionOutputSchema,
      },
    },
    max_output_tokens: maxOutputTokens,
  };

  if (reasoningEffort) {
    request.reasoning = { effort: reasoningEffort };
  }

  return request;
}

function buildReplayOpenAIResponse(generationOutput: JsonObject): JsonObject {
  return {
    id: "waymark-alpha-replay",
    object: "response",
    status: "completed",
    output_text: JSON.stringify(generationOutput),
    usage: {
      input_tokens: 0,
      output_tokens: 0,
      total_tokens: 0,
      input_tokens_details: {
        cached_tokens: 0,
      },
    },
  };
}

function isReplayModeEnabled(): boolean {
  return Deno.env.get("WAYMARK_ALPHA_REPLAY_MODE") === "true";
}

async function callOpenAI(payload: JsonObject): Promise<JsonObject> {
  const apiKey = Deno.env.get("OPENAI_API_KEY");
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not set");
  }

  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`OpenAI API error ${response.status}: ${JSON.stringify(body)}`);
  }
  return body as JsonObject;
}

function extractOutputText(rawResponse: JsonObject): string {
  if (typeof rawResponse.output_text === "string") {
    return rawResponse.output_text;
  }

  const chunks: string[] = [];
  const output = Array.isArray(rawResponse.output) ? rawResponse.output : [];
  for (const outputItem of output) {
    if (!isObject(outputItem)) continue;
    const content = Array.isArray(outputItem.content) ? outputItem.content : [];
    for (const contentItem of content) {
      if (!isObject(contentItem)) continue;
      const type = contentItem.type;
      const text = contentItem.text;
      if ((type === "output_text" || type === "text") && typeof text === "string") {
        chunks.push(text);
      }
    }
  }

  if (chunks.length === 0) {
    throw new Error(`No text output returned by OpenAI (${openAIResponseSummary(rawResponse)})`);
  }
  return chunks.join("\n");
}

function validateMissionOutput(output: JsonObject): ValidationResult {
  const errors: string[] = [];
  if (output.schema_version !== missionOutputSchemaVersion) {
    errors.push(`schema_version must be ${missionOutputSchemaVersion}`);
  }
  if (typeof output.mission_id !== "string" || output.mission_id.length === 0) {
    errors.push("mission_id is required");
  }
  if (typeof output.title !== "string" || output.title.length === 0) {
    errors.push("title is required");
  }
  if (!isObject(output.review_config)) {
    errors.push("review_config is required");
  }
  if (!isObject(output.route) || !Array.isArray(output.route.items) || output.route.items.length === 0) {
    errors.push("route.items must be a non-empty array");
  }
  const items = isObject(output.route) && Array.isArray(output.route.items) ? output.route.items : [];
  for (const [index, rawItem] of items.entries()) {
    if (!isObject(rawItem)) {
      errors.push(`route.items[${index}] must be an object`);
      continue;
    }
    const metadata = rawItem.display_metadata;
    if (!isObject(metadata) || !metadata.artist || !metadata.title) {
      errors.push(`route.items[${index}].display_metadata artist/title are required`);
    }
    const chips = rawItem.feedback_chip_sets;
    if (!isObject(chips)) {
      errors.push(`route.items[${index}].feedback_chip_sets is required`);
    } else {
      for (const operation of ["love", "like", "keep", "not_for_me"]) {
        if (!Array.isArray(chips[operation]) || (chips[operation] as unknown[]).length < 2) {
          errors.push(`route.items[${index}].feedback_chip_sets.${operation} needs at least two chips`);
        }
      }
    }
  }
  return { valid: errors.length === 0, errors };
}

function validateAppMission(mission: JsonObject): ValidationResult {
  const errors: string[] = [];
  if (mission.schema_version !== appMissionSchemaVersion) {
    errors.push(`schema_version must be ${appMissionSchemaVersion}`);
  }
  if (typeof mission.mission_id !== "string" || !/^MIS_[A-Z0-9_]+$/.test(mission.mission_id)) {
    errors.push("mission_id must match MIS_[A-Z0-9_]+");
  }
  if (!Array.isArray(mission.items) || mission.items.length === 0) {
    errors.push("items must be non-empty");
  }
  const items = Array.isArray(mission.items) ? mission.items : [];
  for (const [index, rawItem] of items.entries()) {
    if (!isObject(rawItem)) {
      errors.push(`items[${index}] must be an object`);
      continue;
    }
    if (typeof rawItem.item_id !== "string" || !/^ITEM_[A-Z0-9_]+$/.test(rawItem.item_id)) {
      errors.push(`items[${index}].item_id must match ITEM_[A-Z0-9_]+`);
    }
    if (!isObject(rawItem.apple_music_resolution) || rawItem.apple_music_resolution.status !== "unresolved") {
      errors.push(`items[${index}].apple_music_resolution must start unresolved`);
    }
  }
  return { valid: errors.length === 0, errors };
}

function deriveAppImportStatus(
  generationValidation: ValidationResult,
  appMissionValidation: ValidationResult,
  generation: JsonObject,
): "app_import_candidate" | "review_needed" | "blocked" {
  if (!generationValidation.valid || !appMissionValidation.valid) {
    return "blocked";
  }
  return isReadyForAppImport(generation) ? "app_import_candidate" : "review_needed";
}

function isReadyForAppImport(generation: JsonObject): boolean {
  return isObject(generation.review_config) && generation.review_config.ready_for_app_import === true;
}

function toAppMission(generation: JsonObject): JsonObject {
  const route = generation.route as JsonObject;
  const rawItems = Array.isArray(route.items) ? route.items.filter(isObject) : [];
  const createdAt = new Date().toISOString();
  const appItems = rawItems.map((item, index) => toAppMissionItem(item, index));

  return withoutUndefined({
    schema_version: appMissionSchemaVersion,
    mission_id: appID("MIS", generation.mission_id, "GENERATED_ALPHA"),
    mission_title: String(generation.title),
    mission_version: "v0.1",
    created_at: createdAt,
    mission_type: appItems.some((item) => item.item_type === "album") ? "album_test" : "track_probe",
    recommended_format: "play_items_in_order",
    hypothesis: String(generation.hypothesis),
    inflation_warning:
      "Alpha-generated mission. Treat all route logic and Atlas implications as provisional until reviewed.",
    success_bar: {
      minimum_items_to_resolve: Math.min(3, Math.max(1, appItems.length)),
      minimum_items_to_play: Math.min(3, Math.max(1, appItems.length)),
      minimum_reactions_required: Math.min(3, Math.max(1, appItems.length)),
      requires_physical_iphone: true,
      notes: "Trusted Alpha app-import candidate generated through Supabase/OpenAI.",
    },
    run_instructions: {
      listen_in_order: true,
      shuffle_allowed: false,
      raw_text: route.route_summary ? String(route.route_summary) : undefined,
    },
    post_run_inference_rules: [
      {
        trigger: "After completion, review primary reactions, chips, notes, skips, and resolver status.",
        inference: "Create Signals and possible Atlas updates only through the Alpha review path.",
      },
    ],
    items: appItems,
  });
}

function toAppMissionItem(item: JsonObject, index: number): JsonObject {
  const metadata = isObject(item.display_metadata) ? item.display_metadata : {};
  const searchHint = isObject(item.music_kit_search_hint) ? item.music_kit_search_hint : {};
  const reviewState = isObject(item.review_state) ? item.review_state : {};

  return withoutUndefined({
    item_id: appID("ITEM", item.item_id, `GENERATED_${index + 1}`),
    sequence: index + 1,
    item_type: item.item_type === "album" ? "album" : "track",
    artist: String(metadata.artist ?? searchHint.artist ?? "Unknown Artist"),
    title: String(metadata.title ?? searchHint.title ?? "Unknown Title"),
    album: typeof metadata.album === "string" && metadata.album.length > 0 ? metadata.album : undefined,
    year: typeof metadata.release_year === "number" ? metadata.release_year : undefined,
    why_included: String(item.why_selected ?? item.route_function ?? ""),
    expected_test_signal: [
      item.expected_positive_signal ? `Positive: ${String(item.expected_positive_signal)}` : "",
      item.expected_negative_signal ? `Negative: ${String(item.expected_negative_signal)}` : "",
    ].filter(Boolean).join(" "),
    player_card: {
      flip_side: {
        song_hypothesis: String(item.item_hypothesis ?? ""),
        detail: String(item.route_function ?? ""),
      },
    },
    feedback_chip_sets: toAppFeedbackChipSets(isObject(item.feedback_chip_sets) ? item.feedback_chip_sets : {}),
    apple_music_resolution: {
      status: "unresolved",
      reason: String(searchHint.search_query ?? "generated_alpha_requires_music_kit_resolution"),
      resolver: "not_attempted",
    },
    notes: [
      reviewState.needs_human_review === true ? "Human review requested." : "",
      typeof reviewState.review_notes === "string" ? reviewState.review_notes : "",
    ].filter(Boolean).join(" "),
  });
}

function toAppFeedbackChipSets(chipSets: JsonObject): JsonObject {
  return {
    hit: toAppFeedbackChips(chipSets.love, "hit"),
    partial: toAppFeedbackChips(chipSets.like, "partial"),
    ok_shelf: toAppFeedbackChips(chipSets.keep, "ok_shelf"),
    miss: toAppFeedbackChips(chipSets.not_for_me, "miss"),
  };
}

function toAppFeedbackChips(rawChips: unknown, fallbackPrefix: string): JsonObject[] {
  const chips = Array.isArray(rawChips) ? rawChips.filter(isObject) : [];
  return chips.map((chip, index) => ({
    tag_id: appID("TAG", chip.chip_id, `${fallbackPrefix}_${index + 1}`),
    label: String(chip.label ?? fallbackPrefix),
    description: String(chip.signal_meaning ?? chip.atlas_effect_hint ?? ""),
  }));
}

async function createRun(runId: string, patch: JsonObject): Promise<void> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = getSupabaseServiceKey();
  if (!supabaseUrl || !serviceKey) {
    return;
  }

  const response = await fetch(`${supabaseUrl}/rest/v1/alpha_generation_runs`, {
    method: "POST",
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify({ id: runId, ...patch }),
  });

  if (!response.ok) {
    const body = await response.text();
    console.error(`alpha_generation_runs insert failed: ${response.status} ${body}`);
  }
}

async function updateRun(runId: string, patch: JsonObject): Promise<void> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = getSupabaseServiceKey();
  if (!supabaseUrl || !serviceKey) {
    return;
  }

  const response = await fetch(`${supabaseUrl}/rest/v1/alpha_generation_runs?id=eq.${runId}`, {
    method: "PATCH",
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(patch),
  });

  if (!response.ok) {
    const body = await response.text();
    console.error(`alpha_generation_runs update failed: ${response.status} ${body}`);
  }
}

function getSupabaseServiceKey(): string | undefined {
  const secretKeys = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (secretKeys) {
    try {
      const parsed = JSON.parse(secretKeys) as Record<string, string>;
      return parsed.default ?? Object.values(parsed)[0];
    } catch {
      return undefined;
    }
  }

  return Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
}

function extractUsage(rawResponse: JsonObject): JsonObject {
  const usage = isObject(rawResponse.usage) ? rawResponse.usage : {};
  const inputDetails = isObject(usage.input_tokens_details) ? usage.input_tokens_details : {};
  return {
    input_tokens: usage.input_tokens ?? null,
    cached_input_tokens: inputDetails.cached_tokens ?? null,
    output_tokens: usage.output_tokens ?? null,
    total_tokens: usage.total_tokens ?? null,
  };
}

function openAIResponseSummary(rawResponse: JsonObject): string {
  const status = typeof rawResponse.status === "string" ? rawResponse.status : "unknown_status";
  const output = Array.isArray(rawResponse.output) ? rawResponse.output : [];
  const outputTypes = output
    .filter(isObject)
    .map((outputItem) => {
      const content = Array.isArray(outputItem.content) ? outputItem.content : [];
      const contentTypes = content
        .filter(isObject)
        .map((contentItem) => String(contentItem.type ?? "unknown_content"))
        .join(",");
      return `${String(outputItem.type ?? "unknown_output")}${contentTypes ? `[${contentTypes}]` : ""}`;
    })
    .join(";");
  return `status=${status}; output=${outputTypes || "none"}`;
}

function appID(prefix: string, value: unknown, fallback: string): string {
  const raw = String(value ?? fallback).toUpperCase();
  const slug = raw
    .replace(/[^A-Z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 64);
  if (slug.startsWith(`${prefix}_`)) {
    return slug;
  }
  return `${prefix}_${slug || fallback}`;
}

async function sha256JSON(value: unknown): Promise<string> {
  const encoded = new TextEncoder().encode(JSON.stringify(value));
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function withoutUndefined<T extends JsonObject>(value: T): T {
  return Object.fromEntries(Object.entries(value).filter(([, child]) => child !== undefined)) as T;
}

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function jsonResponse(body: JsonObject, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json",
    },
  });
}
