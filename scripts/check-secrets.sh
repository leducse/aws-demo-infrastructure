#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PATTERN='ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|li_at=[A-Za-z0-9_-]{20,}|-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----'
echo "Scanning source tree (excluding node_modules, cdk.out, .venv) ..."
if grep -rEn "$PATTERN" . \
  --include='*.py' --include='*.ts' --include='*.tsx' --include='*.md' --include='*.json' --include='*.yml' --include='*.yaml' --include='*.sh' \
  --exclude-dir=node_modules --exclude-dir=cdk.out --exclude-dir=.venv --exclude-dir=dist 2>/dev/null; then
  echo "FAIL: possible secrets found"
  exit 1
fi
echo "OK: no common secret patterns in source files."
