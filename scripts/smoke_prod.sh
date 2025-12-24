#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://flowai-backend-3l6u.onrender.com}"

echo "==>Health"
curl -sS "$BASE_URL/health" | cat
echo -e "\n"

echo "==> Extract"
curl -sS -X POST "$BASE_URL/api/extract" \
  -H "Content-Type: application/json" \
  -d '{"source":"text","payload":"uygullamayı aç ardından kaydol butonuna bas ve giriş yap","options":{}}' | cat
echo -e "\n\nOK"
