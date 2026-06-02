"""Load demo configuration from environment + optional Secrets Manager."""

from __future__ import annotations

import os
from dataclasses import dataclass

from portfolio_aws.secrets import get_secret_json


@dataclass(slots=True)
class DemoConfig:
    aws_region: str
    bedrock_model_id: str
    docs_bucket: str | None
    secret_arn: str | None


def load_config(*, require_secret: bool = False) -> DemoConfig:
    """Merge env vars with optional Secrets Manager JSON.

    Secret JSON keys (all optional overrides):
      - bedrock_model_id
      - docs_bucket
    """
    secret_arn = os.environ.get("PORTFOLIO_SECRET_ARN")
    secret: dict = {}
    if secret_arn:
        secret = get_secret_json(secret_arn)

    if require_secret and not secret_arn:
        raise ValueError("PORTFOLIO_SECRET_ARN required for this operation")

    return DemoConfig(
        aws_region=os.environ.get("AWS_REGION", secret.get("aws_region", "us-east-1")),
        bedrock_model_id=os.environ.get(
            "BEDROCK_MODEL_ID",
            secret.get(
                "bedrock_model_id",
                "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            ),
        ),
        docs_bucket=os.environ.get("PORTFOLIO_DOCS_BUCKET", secret.get("docs_bucket")),
        secret_arn=secret_arn,
    )
