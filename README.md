# Portfolio AWS Demos — CDK + Real Bedrock

Deploys **real** AWS resources for portfolio case-study demos: S3 for artifacts,
Secrets Manager for config (no keys in git), Lambda that calls **Amazon Bedrock**,
and an HTTP API to invoke the Tableau documentation generator.

## What you learn here

| AWS service | Role in this project | CloudFormation? |
|-------------|----------------------|-----------------|
| **CDK** (TypeScript) | You write infra as code | `cdk synth` → template |
| **CloudFormation** | Engine that creates/updates stacks | Yes — every `cdk deploy` |
| **S3** | Store generated workbook docs | `AWS::S3::Bucket` |
| **Secrets Manager** | Bedrock model id + config JSON | `AWS::SecretsManager::Secret` |
| **IAM** | Lambda role: S3 read/write, Bedrock invoke, secret read | `AWS::IAM::Role` |
| **Lambda** | Runs Python that calls Bedrock Converse | `AWS::Lambda::Function` |
| **API Gateway** | `POST /generate` to trigger Lambda | `AWS::ApiGatewayV2::*` |
| **CloudWatch Logs** | Lambda logs (automatic) | Log groups |

Read the full tour: [`docs/CDK_WALKTHROUGH.md`](docs/CDK_WALKTHROUGH.md).

Diagrams: [`docs/DRAWIO_MCP.md`](docs/DRAWIO_MCP.md) + `docs/architecture/`.

## Prerequisites

- Node 20+, AWS CLI, AWS CDK CLI (`npm install -g aws-cdk`)
- Bootstrapped account: `cdk bootstrap aws://ACCOUNT/us-east-1`
- Bedrock model access enabled (Claude Sonnet inference profile in your region)
- AWS profile with permission to deploy IAM, Lambda, S3, Secrets Manager, API Gateway

## Deploy

```bash
cd infra
npm ci
npm run build
npx cdk deploy --require-approval never
```

After deploy, set the secret value (CDK creates an **empty** secret shell — you fill it once):

```bash
SECRET_ARN=$(aws cloudformation describe-stacks --stack-name PortfolioDemosStack \
  --query "Stacks[0].Outputs[?OutputKey=='SecretArn'].OutputValue" --output text)

aws secretsmanager put-secret-value --secret-id "$SECRET_ARN" --secret-string '{
  "bedrock_model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "docs_bucket": "REPLACE_WITH_DOCS_BUCKET_OUTPUT"
}'
```

## Test Bedrock (local, using your profile)

```bash
pip install -e ../libs/portfolio_aws
export PORTFOLIO_SECRET_ARN="$SECRET_ARN"
export AWS_REGION=us-east-1
python scripts/bedrock_smoke_test.py
```

## Test via API (after deploy)

```bash
API_URL=$(aws cloudformation describe-stacks --stack-name PortfolioDemosStack \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)

curl -s -X POST "$API_URL/generate" \
  -H 'Content-Type: application/json' \
  -d @../tableau-workbook-knowledge-platform/output/metadata.json | jq .
```

## CI/CD

GitHub Actions in [`.github/workflows/`](.github/workflows/):

- **cdk-synth.yml** — every PR: install, build, `cdk synth` (validates CloudFormation)
- **cdk-deploy.yml** — manual `workflow_dispatch` with OIDC to AWS (see walkthrough)

## Cost expectation

Small demo usage is typically **under a few dollars/month** (S3 + Secrets Manager + occasional Lambda + Bedrock tokens). Tear down with `cdk destroy` when idle.

## Related portfolio repos

| Repo | Uses this stack |
|------|-----------------|
| `tableau-workbook-knowledge-platform` | `DOC_GENERATOR=bedrock` + `PORTFOLIO_SECRET_ARN` |
| `tableau-quicksight-migration-assistant` | Next: wire `GENAI_PROVIDER=bedrock` to real Converse |
| `mcp-query-governance` | Future: RDS/SageMaker path (separate stack) |
