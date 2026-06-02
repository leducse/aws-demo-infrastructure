"""Read configuration from AWS Secrets Manager (never commit secret values)."""

from __future__ import annotations

import json
import os
from typing import Any


def get_secret_json(secret_arn: str | None = None, *, region: str | None = None) -> dict[str, Any]:
    """Fetch and parse a Secrets Manager secret as JSON.

    The secret ARN comes from ``PORTFOLIO_SECRET_ARN`` or the ``secret_arn`` argument.
    Credentials use the standard AWS chain (profile, env, SSO, Lambda role).
    """
    arn = secret_arn or os.environ.get("PORTFOLIO_SECRET_ARN")
    if not arn:
        raise ValueError(
            "PORTFOLIO_SECRET_ARN is not set. Deploy the CDK stack or export the ARN from stack outputs."
        )

    import boto3

    client = boto3.client("secretsmanager", region_name=region or os.environ.get("AWS_REGION", "us-east-1"))
    response = client.get_secret_value(SecretId=arn)
    raw = response.get("SecretString")
    if not raw:
        raise ValueError(f"Secret {arn} has no SecretString payload")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Portfolio secret must be a JSON object")
    return data
