#!/bin/sh

set -e

HOST_PORT="${FIRESTORE_EMULATOR_HOST:-firestore:8080}"
export HOST="${HOST_PORT%:*}"
export PORT="${HOST_PORT#*:}"
MAX_RETRIES="${FIRESTORE_WAIT_MAX_RETRIES:-60}"

printf '%s\n' "Waiting for Firestore emulator at ${HOST}:${PORT}..."

i=0
while true; do
  python - <<'PY' && break
import os
import socket
import sys

host = os.environ.get("HOST", "firestore")
port = int(os.environ.get("PORT", "8080"))
s = socket.socket()
s.settimeout(1)
try:
    s.connect((host, port))
except OSError:
    sys.exit(1)
else:
    sys.exit(0)
finally:
    s.close()
PY
  i=$((i+1))
  printf '%s\n' "Attempt ${i}/${MAX_RETRIES}: not ready"
  if [ "$i" -ge "$MAX_RETRIES" ]; then
    printf '%s\n' "Firestore not ready after $((MAX_RETRIES * 2)) seconds"
    exit 1
  fi
  sleep 2
done

printf '%s\n' "Firestore emulator is ready"
