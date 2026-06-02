"""Lambda: Tableau workbook metadata JSON → Bedrock draft/refine → S3.

Invoked via API Gateway POST /generate with the metadata document as JSON body.
Uses portfolio_aws (vendored under lambdas/shared/) for Secrets Manager + Converse.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Lambda asset layout: shared/portfolio_aws next to tableau_doc/
_SHARED = Path(__file__).resolve().parent.parent / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from portfolio_aws.bedrock import BedrockConverse  # noqa: E402
from portfolio_aws.config import load_config  # noqa: E402

_DRAFT_SYSTEM = "You are a BI documentation writer. Use only the provided metadata."
_DRAFT_USER = """Write markdown documentation for this Tableau workbook metadata.
Include: Purpose, Metrics & Calculated Fields, Parameters, Data Sources, Dashboards.
Do not invent fields.

Metadata JSON:
{metadata}
"""

_REFINE_SYSTEM = "You are a BI documentation editor. Ground every claim in the metadata."
_REFINE_USER = """Refine the draft. Remove unsupported claims. Keep sections:
Purpose, Metrics & Calculated Fields, Parameters, Data Sources, Dashboards.

Metadata:
{metadata}

Draft:
{draft}
"""


def handler(event, context):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64

        body = base64.b64decode(body).decode("utf-8")
    metadata = json.loads(body)

    config = load_config(require_secret=True)
    llm = BedrockConverse(config)

    meta_str = json.dumps(metadata, indent=2)
    draft = llm.complete(_DRAFT_USER.format(metadata=meta_str), system=_DRAFT_SYSTEM).text
    refined = llm.complete(
        _REFINE_USER.format(metadata=meta_str, draft=draft),
        system=_REFINE_SYSTEM,
    ).text

    workbook_id = metadata.get("workbook_id", "unknown")
    key = f"workbooks/{workbook_id}/generated/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"

    import boto3

    s3 = boto3.client("s3", region_name=config.aws_region)
    bucket = config.docs_bucket or os.environ["PORTFOLIO_DOCS_BUCKET"]
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=refined.encode("utf-8"),
        ContentType="text/markdown",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "workbook_id": workbook_id,
                "s3_bucket": bucket,
                "s3_key": key,
                "generated_by": "bedrock-lambda",
                "model_id": config.bedrock_model_id,
                "markdown_preview": refined[:500] + ("..." if len(refined) > 500 else ""),
            }
        ),
    }
