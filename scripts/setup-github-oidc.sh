#!/usr/bin/env bash
# One-time: GitHub Actions OIDC → IAM role for cdk-deploy.yml
set -euo pipefail

ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
REGION="${AWS_REGION:-us-east-1}"
REPO="${GITHUB_REPO:-leducse/portfolio-aws-demos}"
ROLE_NAME="${ROLE_NAME:-GitHubActionsPortfolioAwsDemosDeploy}"
OIDC_URL="https://token.actions.githubusercontent.com"
# GitHub's documented thumbprint (also fetchable via openssl against token.actions.githubusercontent.com)
THUMBPRINT="${GITHUB_OIDC_THUMBPRINT:-6938fd4d98bab03fa91895cebd4c574ef06bb7f3}"

echo "Account: $ACCOUNT_ID  Region: $REGION  Repo: $REPO"

if ! aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')]" --output text | grep -q .; then
  echo "Creating OIDC provider..."
  aws iam create-open-id-connect-provider \
    --url "$OIDC_URL" \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list "$THUMBPRINT"
else
  echo "OIDC provider already exists."
fi

TRUST_FILE="$(mktemp)"
POLICY_ATTACH=""

cat >"$TRUST_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${REPO}:*"
        }
      }
    }
  ]
}
EOF

if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo "Updating trust policy on existing role $ROLE_NAME..."
  aws iam update-assume-role-policy --role-name "$ROLE_NAME" --policy-document "file://${TRUST_FILE}"
else
  echo "Creating IAM role $ROLE_NAME..."
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --description "GitHub Actions OIDC deploy for ${REPO} (CDK)" \
    --assume-role-policy-document "file://${TRUST_FILE}"
fi

rm -f "$TRUST_FILE"

# CDK deploy needs CloudFormation, IAM pass-role, Lambda, API GW, Secrets Manager, S3, logs, SSM bootstrap params.
for POLICY in \
  arn:aws:iam::aws:policy/PowerUserAccess \
  arn:aws:iam::aws:policy/IAMFullAccess; do
  POLICY_NAME=$(basename "$POLICY")
  if ! aws iam list-attached-role-policies --role-name "$ROLE_NAME" \
    --query "AttachedPolicies[?PolicyArn=='${POLICY}']" --output text | grep -q .; then
    echo "Attaching $POLICY_NAME..."
    aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn "$POLICY"
  else
    echo "Already attached: $POLICY_NAME"
  fi
done

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo ""
echo "ROLE_ARN=$ROLE_ARN"
echo "AWS_REGION=$REGION"
echo ""
echo "Setting GitHub repository secrets..."
gh secret set AWS_ROLE_ARN --repo "$REPO" --body "$ROLE_ARN"
gh secret set AWS_REGION --repo "$REPO" --body "$REGION"
echo "Done. Run deploy from: https://github.com/${REPO}/actions/workflows/cdk-deploy.yml"
