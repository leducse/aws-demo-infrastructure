#!/usr/bin/env bash
# Copy portfolio_aws library into lambdas/shared for Lambda deployment asset.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rsync -a --delete "$ROOT/../libs/portfolio_aws/src/portfolio_aws/" "$ROOT/lambdas/shared/portfolio_aws/"
echo "Synced portfolio_aws → lambdas/shared/portfolio_aws/"
