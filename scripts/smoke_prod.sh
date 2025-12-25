#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${1:-https://flowai-backend-3l6u.onrender.com}"

# ---- settings (tweakable) ----
CONNECT_TIMEOUT="${CONNECT_TIMEOUT:-5}"  # seconds
MAX_TIME="${MAX_TIME:-15}"              # seconds
RETRIES="${RETRIES:-3}"                 # total attempts
RETRY_DELAY="${RETRY_DELAY:-2}"         # seconds between attempts

# Temp files
TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

fail() {
  echo "❌ $*" >&2
  exit 1
}

request() {
  # usage: request <name> <method> <url> [data_json]
  local name="$1"
  local method="$2"
  local url="$3"
  local data="${4:-}"
  local body_file="$TMP_DIR/${name}_body.json"
  local code_file="$TMP_DIR/${name}_code.txt"

  echo "==> $name ($method $url)"

  # Curl: write body to file + http status to separate file
  if [[ -n "$data" ]]; then
    curl -sS \
      --connect-timeout "$CONNECT_TIMEOUT" \
      --max-time "$MAX_TIME" \
      --retry "$RETRIES" \
      --retry-delay "$RETRY_DELAY" \
      --retry-all-errors \
      -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$data" \
      -o "$body_file" \
      -w "%{http_code}" > "$code_file"
  else
    curl -sS \
      --connect-timeout "$CONNECT_TIMEOUT" \
      --max-time "$MAX_TIME" \
      --retry "$RETRIES" \
      --retry-delay "$RETRY_DELAY" \
      --retry-all-errors \
      -X "$method" "$url" \
      -o "$body_file" \
      -w "%{http_code}" > "$code_file"
  fi

  local code
  code="$(cat "$code_file")"

  # Show body (for logs)
  cat "$body_file"
  echo -e "\n"

  # Hard assert
  if [[ "$code" != "200" ]]; then
    fail "$name failed: HTTP $code"
  fi
}

# ---- calls ----
request "Health" "GET" "$BASE_URL/health"

payload='{"source":"text","payload":"uygullamayı aç ardından kaydol butonuna bas ve giriş yap","options":{}}'
request "Extract" "POST" "$BASE_URL/api/extract" "$payload"

echo "✅ OK"
