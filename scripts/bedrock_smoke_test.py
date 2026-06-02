#!/usr/bin/env python3
"""Verify Bedrock + Secrets Manager from your laptop (uses AWS profile, not git secrets)."""

from __future__ import annotations

import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[2] / "libs" / "portfolio_aws" / "src"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from portfolio_aws import BedrockConverse, load_config  # noqa: E402


def main() -> None:
    cfg = load_config(require_secret=True)
    print(f"Region: {cfg.aws_region}")
    print(f"Model:  {cfg.bedrock_model_id}")
    resp = BedrockConverse(cfg).complete(
        "Reply with exactly one line: portfolio-bedrock-ok",
        system="You are a test harness.",
        max_tokens=64,
    )
    print("Response:", resp.text.strip())
    print("Tokens:", resp.total_tokens)


if __name__ == "__main__":
    main()
