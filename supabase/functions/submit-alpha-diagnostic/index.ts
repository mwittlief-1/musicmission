declare const Deno: {
  serve(handler: (request: Request) => Response | Promise<Response>): void;
  env: { get(key: string): string | undefined };
};

type JsonObject = Record<string, unknown>;

type DiagnosticConsent = {
  diagnostic_upload_allowed?: boolean;
  terms_version?: string;
  accepted_at?: string;
};

type AlphaDiagnosticUploadRequest = {
  client_artifact_id?: string;
  tester_alias?: string;
  artifact_type?: string;
  schema_version?: string;
  survey_session_id?: string | null;
  client_request_id?: string | null;
  generation_run_id?: string | null;
  mission_id?: string | null;
  source_app_version?: string;
  source_app_build?: string;
  redaction_level?: string;
  upload_cadence?: string;
  client_created_at?: string;
  consent?: DiagnosticConsent;
  payload?: JsonObject;
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

const allowedArtifactTypes = new Set([
  "apple_music_signal_payload",
  "survey_page_selection_audit",
  "survey_evidence_export",
  "mission_generation_request_packet",
  "mission_generation_result",
  "mission_import_result",
  "client_state_snapshot",
  "client_error_event",
]);

const allowedRedactionLevels = new Set([
  "support_diagnostic",
  "pm_summary",
  "redacted",
]);

const allowedUploadCadences = new Set([
  "manual_share",
  "after_saved_evidence",
  "scheduled",
]);

Deno.serve(async (request: Request) => {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (request.method !== "POST") {
    return jsonResponse({ error: "method_not_allowed" }, 405);
  }

  const receivedAt = new Date().toISOString();
  const uploadId = crypto.randomUUID();
  let input: AlphaDiagnosticUploadRequest;

  try {
    input = await request.json();
  } catch {
    return jsonResponse({ upload_id: uploadId, error: "invalid_json" }, 400);
  }

  const validation = validateUpload(input);
  if (!validation.valid) {
    return jsonResponse({ upload_id: uploadId, error: "invalid_input", validation }, 400);
  }

  const userID = userIDFromAuthorization(request.headers.get("Authorization"));
  const payloadSha256 = await sha256JSON(input.payload);

  try {
    const persisted = await persistDiagnosticArtifact(uploadId, {
      client_artifact_id: input.client_artifact_id,
      tester_alias: input.tester_alias,
      user_id: userID,
      artifact_type: input.artifact_type,
      schema_version: input.schema_version,
      survey_session_id: normalizeOptionalText(input.survey_session_id),
      client_request_id: normalizeOptionalText(input.client_request_id),
      generation_run_id: normalizeOptionalText(input.generation_run_id),
      mission_id: normalizeOptionalText(input.mission_id),
      source_app_version: input.source_app_version,
      source_app_build: input.source_app_build,
      redaction_level: normalizeRedactionLevel(input.redaction_level),
      upload_cadence: normalizeUploadCadence(input.upload_cadence),
      consent_terms_version: input.consent?.terms_version,
      consent_accepted_at: input.consent?.accepted_at,
      payload: input.payload,
      payload_sha256: payloadSha256,
      client_created_at: input.client_created_at,
      received_at: receivedAt,
    });

    return jsonResponse({
      upload_id: uploadId,
      status: persisted ? "accepted" : "accepted_not_persisted_local_mode",
      received_at: receivedAt,
      artifact_type: input.artifact_type,
      schema_version: input.schema_version,
      payload_sha256: payloadSha256,
      user_id_present: userID !== null,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return jsonResponse({ upload_id: uploadId, status: "failed", error: message }, 500);
  }
});

function validateUpload(input: AlphaDiagnosticUploadRequest): ValidationResult {
  const errors: string[] = [];

  if (typeof input.client_artifact_id !== "string" || input.client_artifact_id.trim().length === 0) {
    errors.push("client_artifact_id is required");
  }

  if (typeof input.artifact_type !== "string" || !allowedArtifactTypes.has(input.artifact_type)) {
    errors.push(`artifact_type must be one of ${Array.from(allowedArtifactTypes).join(", ")}`);
  }

  if (typeof input.schema_version !== "string" || input.schema_version.trim().length === 0) {
    errors.push("schema_version is required");
  }

  if (!isObject(input.payload)) {
    errors.push("payload must be an object");
  }

  if (input.redaction_level !== undefined && !allowedRedactionLevels.has(input.redaction_level)) {
    errors.push(`redaction_level must be one of ${Array.from(allowedRedactionLevels).join(", ")}`);
  }

  if (input.upload_cadence !== undefined && !allowedUploadCadences.has(input.upload_cadence)) {
    errors.push(`upload_cadence must be one of ${Array.from(allowedUploadCadences).join(", ")}`);
  }

  if (input.generation_run_id !== undefined && input.generation_run_id !== null && !isUUID(input.generation_run_id)) {
    errors.push("generation_run_id must be a UUID when supplied");
  }

  if (!isObject(input.consent)) {
    errors.push("consent is required");
  } else {
    if (input.consent.diagnostic_upload_allowed !== true) {
      errors.push("consent.diagnostic_upload_allowed must be true");
    }
    if (typeof input.consent.terms_version !== "string" || input.consent.terms_version.trim().length === 0) {
      errors.push("consent.terms_version is required");
    }
    if (typeof input.consent.accepted_at !== "string" || Number.isNaN(Date.parse(input.consent.accepted_at))) {
      errors.push("consent.accepted_at must be an ISO timestamp");
    }
  }

  if (input.client_created_at !== undefined && Number.isNaN(Date.parse(input.client_created_at))) {
    errors.push("client_created_at must be an ISO timestamp when supplied");
  }

  return { valid: errors.length === 0, errors };
}

async function persistDiagnosticArtifact(uploadId: string, artifact: JsonObject): Promise<boolean> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = getSupabaseServiceKey();
  if (!supabaseUrl || !serviceKey) {
    return false;
  }

  const response = await fetch(
    `${supabaseUrl}/rest/v1/alpha_client_diagnostic_artifacts?on_conflict=client_artifact_id`,
    {
      method: "POST",
      headers: {
        apikey: serviceKey,
        Authorization: `Bearer ${serviceKey}`,
        "Content-Type": "application/json",
        Prefer: "resolution=ignore-duplicates,return=minimal",
      },
      body: JSON.stringify({ id: uploadId, ...withoutUndefined(artifact) }),
    },
  );

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`alpha_client_diagnostic_artifacts persist failed: ${response.status} ${body}`);
  }

  return true;
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

function normalizeOptionalText(value: unknown): string | undefined {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : undefined;
}

function normalizeRedactionLevel(value: unknown): string {
  return typeof value === "string" && allowedRedactionLevels.has(value) ? value : "support_diagnostic";
}

function normalizeUploadCadence(value: unknown): string {
  return typeof value === "string" && allowedUploadCadences.has(value) ? value : "manual_share";
}

function userIDFromAuthorization(header: string | null): string | null {
  if (!header) return null;
  const match = header.match(/^Bearer\s+(.+)$/i);
  const token = match?.[1];
  if (!token) return null;

  const parts = token.split(".");
  if (parts.length < 2) return null;

  try {
    const payload = JSON.parse(atob(toBase64(parts[1]))) as JsonObject;
    return typeof payload.sub === "string" && payload.sub.length > 0 ? payload.sub : null;
  } catch {
    return null;
  }
}

function toBase64(base64URL: string): string {
  const base64 = base64URL.replace(/-/g, "+").replace(/_/g, "/");
  const padding = base64.length % 4;
  return padding === 0 ? base64 : `${base64}${"=".repeat(4 - padding)}`;
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

function isUUID(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
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
