# PortfolioDemosStack — architecture (draft)

Use the **draw.io MCP** (`drawio` server in Cursor) to produce a polished diagram with AWS icons. This file is the source-of-truth checklist until `.drawio` is exported.

## Components

| Layer | Service | Responsibility |
|-------|---------|----------------|
| Edge | API Gateway HTTP API | `POST /generate` |
| Compute | Lambda `TableauDocGenerator` | Metadata JSON → Bedrock draft/refine → S3 |
| AI | Amazon Bedrock (Converse) | Claude via inference profile |
| Config | Secrets Manager | `bedrock_model_id`, `docs_bucket` |
| Storage | S3 `PortfolioDocs` | Versioned markdown artifacts |
| Ops | CloudWatch Logs | Lambda execution logs |

## Data flow

```
Client (curl / local pipeline)
  → API Gateway POST /generate
  → Lambda handler
      → Secrets Manager (read config)
      → Bedrock Converse (draft + refine)
      → S3 PutObject (markdown)
  ← JSON { s3_bucket, s3_key, preview }
```

## draw.io prompt (paste into Cursor)

> Using the drawio MCP, search_shapes for AWS API Gateway, Lambda, Bedrock, Secrets Manager, and S3.
> Create a left-to-right architecture diagram for the flow above.
> Export instructions: save as `docs/architecture/portfolio-demos.drawio`.

## CloudFormation cross-reference

After `cdk synth`, open `infra/cdk.out/PortfolioDemosStack.template.json` and search for:

- `AWS::S3::Bucket`
- `AWS::SecretsManager::Secret`
- `AWS::Lambda::Function`
- `AWS::ApiGatewayV2::Api`

See [`../CDK_WALKTHROUGH.md`](../CDK_WALKTHROUGH.md).
