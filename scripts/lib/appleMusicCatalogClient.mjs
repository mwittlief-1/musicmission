import crypto from "node:crypto";
import fs from "node:fs";
import https from "node:https";
import os from "node:os";
import path from "node:path";

export const DEFAULT_ENV_PATH = path.join(
  os.homedir(),
  ".config/cartenza/apple-music/catalog-resolver.env",
);

export const DEFAULT_CATALOG_BASE_URL = "https://api.music.apple.com";

const DEFAULT_USER_AGENT = "CartenzaAppleMusicCatalogClient/0.1";
const DEFAULT_TOKEN_TTL_SECONDS = 60 * 60;
const MAX_APPLE_MUSIC_TOKEN_TTL_SECONDS = 15777000;
const RETRYABLE_STATUS_CODES = new Set([429, 500, 502, 503, 504]);

export function loadCatalogResolverEnv(envPath = DEFAULT_ENV_PATH, baseEnv = process.env) {
  const loaded = { ...baseEnv };
  if (!fs.existsSync(envPath)) return loaded;

  const envText = fs.readFileSync(envPath, "utf8");
  for (const line of envText.split(/\r?\n/u)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const separatorIndex = trimmed.indexOf("=");
    if (separatorIndex < 1) continue;

    const key = trimmed.slice(0, separatorIndex).trim();
    const rawValue = trimmed.slice(separatorIndex + 1).trim();
    loaded[key] = unquoteEnvValue(rawValue);
  }

  return loaded;
}

export function readAppleMusicCatalogConfig(options = {}) {
  const env = options.env ?? loadCatalogResolverEnv(options.envPath);
  const teamId = firstPresent(options.teamId, env.APPLE_MUSIC_TEAM_ID, env.APPLE_TEAM_ID);
  const keyId = firstPresent(options.keyId, env.APPLE_MUSIC_KEY_ID, env.APPLE_KEY_ID);
  const privateKeyPath = firstPresent(
    options.privateKeyPath,
    env.APPLE_MUSIC_PRIVATE_KEY_PATH,
    env.APPLE_PRIVATE_KEY_PATH,
  );

  return {
    teamId,
    keyId,
    privateKeyPath,
    storefront: firstPresent(options.storefront, env.APPLE_MUSIC_STOREFRONT, "us"),
    baseUrl: firstPresent(options.baseUrl, env.APPLE_MUSIC_CATALOG_BASE_URL, DEFAULT_CATALOG_BASE_URL),
    userAgent: firstPresent(options.userAgent, env.APPLE_MUSIC_USER_AGENT, DEFAULT_USER_AGENT),
    tokenTtlSeconds: parsePositiveInteger(
      firstPresent(options.tokenTtlSeconds, env.APPLE_MUSIC_TOKEN_TTL_SECONDS),
      DEFAULT_TOKEN_TTL_SECONDS,
    ),
    timeoutMs: parsePositiveInteger(firstPresent(options.timeoutMs, env.APPLE_MUSIC_TIMEOUT_MS), 20000),
    maxRetries: parseNonNegativeInteger(firstPresent(options.maxRetries, env.APPLE_MUSIC_MAX_RETRIES), 3),
    retryBaseDelayMs: parsePositiveInteger(
      firstPresent(options.retryBaseDelayMs, env.APPLE_MUSIC_RETRY_BASE_DELAY_MS),
      500,
    ),
    retryMaxDelayMs: parsePositiveInteger(
      firstPresent(options.retryMaxDelayMs, env.APPLE_MUSIC_RETRY_MAX_DELAY_MS),
      30000,
    ),
  };
}

export function generateDeveloperToken(options = {}) {
  const config = readAppleMusicCatalogConfig(options);
  requireConfigValue(config.teamId, "APPLE_MUSIC_TEAM_ID");
  requireConfigValue(config.keyId, "APPLE_MUSIC_KEY_ID");
  requireConfigValue(config.privateKeyPath, "APPLE_MUSIC_PRIVATE_KEY_PATH");

  const privateKey = fs.readFileSync(resolveHomePath(config.privateKeyPath), "utf8");
  const now = Math.floor(Date.now() / 1000);
  const ttlSeconds = Math.min(config.tokenTtlSeconds, MAX_APPLE_MUSIC_TOKEN_TTL_SECONDS);
  const header = { alg: "ES256", kid: config.keyId, typ: "JWT" };
  const payload = { iss: config.teamId, iat: now, exp: now + ttlSeconds };
  const signingInput = `${base64UrlJson(header)}.${base64UrlJson(payload)}`;
  const signer = crypto.createSign("SHA256");
  signer.update(signingInput);
  signer.end();
  const derSignature = signer.sign(privateKey);
  const joseSignature = derToJoseSignature(derSignature, 32);

  return `${signingInput}.${base64Url(joseSignature)}`;
}

export function createAppleMusicCatalogClient(options = {}) {
  const config = readAppleMusicCatalogConfig(options);
  let cachedToken = null;
  let cachedTokenExpiresAt = 0;

  function getDeveloperToken() {
    if (options.developerToken) return options.developerToken;

    const nowMs = Date.now();
    if (cachedToken && cachedTokenExpiresAt - 60000 > nowMs) return cachedToken;

    cachedToken = generateDeveloperToken(config);
    cachedTokenExpiresAt = nowMs + Math.min(config.tokenTtlSeconds, MAX_APPLE_MUSIC_TOKEN_TTL_SECONDS) * 1000;
    return cachedToken;
  }

  return {
    catalogGet(endpoint, query = {}, requestOptions = {}) {
      return catalogGet(endpoint, query, {
        ...config,
        ...requestOptions,
        developerToken: getDeveloperToken(),
      });
    },
    catalogSearch(searchOptions = {}, requestOptions = {}) {
      return catalogSearch(searchOptions, {
        ...config,
        ...requestOptions,
        developerToken: getDeveloperToken(),
      });
    },
    generateDeveloperToken: getDeveloperToken,
  };
}

export async function catalogGet(endpoint, query = {}, options = {}) {
  const config = readAppleMusicCatalogConfig(options);
  const developerToken = options.developerToken ?? generateDeveloperToken(config);
  const url = buildCatalogUrl(endpoint, query, config);

  return requestJson(url, {
    developerToken,
    userAgent: config.userAgent,
    timeoutMs: config.timeoutMs,
    maxRetries: config.maxRetries,
    retryBaseDelayMs: config.retryBaseDelayMs,
    retryMaxDelayMs: config.retryMaxDelayMs,
  });
}

export async function catalogSearch(searchOptions = {}, options = {}) {
  const config = readAppleMusicCatalogConfig({ ...options, storefront: searchOptions.storefront });
  const term = firstPresent(searchOptions.term, searchOptions.q);
  requireConfigValue(term, "search term");

  const query = {
    term,
    types: normalizeTypes(searchOptions.types),
    limit: searchOptions.limit,
    offset: searchOptions.offset,
    l: searchOptions.l,
    with: searchOptions.with,
  };

  return catalogGet(`/v1/catalog/${encodeURIComponent(config.storefront)}/search`, query, {
    ...config,
    developerToken: options.developerToken,
  });
}

export function buildCatalogUrl(endpoint, query = {}, options = {}) {
  const config = readAppleMusicCatalogConfig(options);
  const baseUrl = new URL(config.baseUrl);
  const url = new URL(normalizeCatalogEndpoint(endpoint, config.storefront), baseUrl);

  for (const [key, value] of Object.entries(query ?? {})) {
    if (value === undefined || value === null || value === "") continue;
    if (Array.isArray(value)) {
      if (value.length > 0) url.searchParams.set(key, value.join(","));
    } else {
      url.searchParams.set(key, String(value));
    }
  }

  return url;
}

async function requestJson(url, options) {
  let attempt = 0;

  while (true) {
    const response = await httpsGetJson(url, options);
    if (!RETRYABLE_STATUS_CODES.has(response.statusCode) || attempt >= options.maxRetries) {
      if (response.statusCode >= 200 && response.statusCode < 300) return response.body;
      throw new Error(`Apple Music catalog request failed with HTTP ${response.statusCode}`);
    }

    const retryDelayMs = retryDelayForAttempt(response.headers, attempt, options);
    await sleep(retryDelayMs);
    attempt += 1;
  }
}

function httpsGetJson(url, options) {
  return new Promise((resolve, reject) => {
    const request = https.request(url, {
      method: "GET",
      timeout: options.timeoutMs,
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${options.developerToken}`,
        "User-Agent": options.userAgent,
      },
    }, (response) => {
      const chunks = [];
      response.setEncoding("utf8");
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => {
        const text = chunks.join("");
        let body = null;
        if (text) {
          try {
            body = JSON.parse(text);
          } catch {
            body = null;
          }
        }
        return resolve({ statusCode: response.statusCode ?? 0, headers: response.headers, body });
      });
    });

    request.on("timeout", () => {
      request.destroy(new Error("Apple Music catalog request timed out"));
    });
    request.on("error", reject);
    request.end();
  });
}

function normalizeCatalogEndpoint(endpoint, storefront) {
  requireConfigValue(endpoint, "catalog endpoint");
  const endpointText = String(endpoint);
  if (endpointText.startsWith("http://") || endpointText.startsWith("https://")) return endpointText;
  if (endpointText.startsWith("/v1/")) return endpointText;
  if (endpointText.startsWith("v1/")) return `/${endpointText}`;
  return `/v1/catalog/${encodeURIComponent(storefront)}/${endpointText.replace(/^\/+/u, "")}`;
}

function normalizeTypes(types) {
  if (Array.isArray(types)) return types.join(",");
  return firstPresent(types, "songs,albums,artists");
}

function retryDelayForAttempt(headers, attempt, options) {
  const retryAfter = retryAfterMs(headers["retry-after"]);
  if (retryAfter !== null) return Math.min(retryAfter, options.retryMaxDelayMs);

  const exponentialDelay = options.retryBaseDelayMs * 2 ** attempt;
  const jitter = Math.floor(Math.random() * Math.max(1, Math.round(exponentialDelay * 0.2)));
  return Math.min(exponentialDelay + jitter, options.retryMaxDelayMs);
}

function retryAfterMs(value) {
  if (!value) return null;
  const retryAfter = Array.isArray(value) ? value[0] : value;
  const seconds = Number(retryAfter);
  if (Number.isFinite(seconds) && seconds >= 0) return seconds * 1000;

  const dateMs = Date.parse(retryAfter);
  if (Number.isFinite(dateMs)) return Math.max(0, dateMs - Date.now());
  return null;
}

function derToJoseSignature(derSignature, partLength) {
  let offset = 0;
  if (derSignature[offset++] !== 0x30) throw new Error("Invalid ES256 signature");
  const sequenceLength = readDerLength(derSignature, offset);
  offset = sequenceLength.offset;
  if (sequenceLength.length + offset !== derSignature.length) throw new Error("Invalid ES256 signature length");

  const r = readDerInteger(derSignature, offset);
  offset = r.offset;
  const s = readDerInteger(derSignature, offset);

  return Buffer.concat([leftPadUnsigned(r.value, partLength), leftPadUnsigned(s.value, partLength)]);
}

function readDerInteger(buffer, offset) {
  if (buffer[offset++] !== 0x02) throw new Error("Invalid ES256 signature integer");
  const length = readDerLength(buffer, offset);
  offset = length.offset;
  return { value: buffer.subarray(offset, offset + length.length), offset: offset + length.length };
}

function readDerLength(buffer, offset) {
  const first = buffer[offset++];
  if (first < 0x80) return { length: first, offset };

  const bytes = first & 0x7f;
  if (bytes < 1 || bytes > 4) throw new Error("Invalid ES256 signature length");

  let length = 0;
  for (let index = 0; index < bytes; index += 1) {
    length = (length << 8) | buffer[offset++];
  }
  return { length, offset };
}

function leftPadUnsigned(value, partLength) {
  let normalized = value;
  while (normalized.length > partLength && normalized[0] === 0) {
    normalized = normalized.subarray(1);
  }
  if (normalized.length > partLength) throw new Error("Invalid ES256 signature component length");
  if (normalized.length === partLength) return normalized;
  return Buffer.concat([Buffer.alloc(partLength - normalized.length), normalized]);
}

function base64UrlJson(value) {
  return base64Url(Buffer.from(JSON.stringify(value), "utf8"));
}

function base64Url(value) {
  return Buffer.from(value)
    .toString("base64")
    .replace(/=/gu, "")
    .replace(/\+/gu, "-")
    .replace(/\//gu, "_");
}

function unquoteEnvValue(value) {
  if (value.length < 2) return value;
  const quote = value[0];
  if ((quote !== "\"" && quote !== "'") || value[value.length - 1] !== quote) return value;
  const inner = value.slice(1, -1);
  return quote === "\"" ? inner.replace(/\\n/gu, "\n").replace(/\\"/gu, "\"").replace(/\\\\/gu, "\\") : inner;
}

function resolveHomePath(filePath) {
  if (filePath === "~") return os.homedir();
  if (filePath.startsWith("~/")) return path.join(os.homedir(), filePath.slice(2));
  return filePath;
}

function firstPresent(...values) {
  return values.find((value) => value !== undefined && value !== null && value !== "");
}

function requireConfigValue(value, label) {
  if (value === undefined || value === null || value === "") {
    throw new Error(`Missing required Apple Music catalog setting: ${label}`);
  }
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

function parseNonNegativeInteger(value, fallback) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed >= 0 ? parsed : fallback;
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
