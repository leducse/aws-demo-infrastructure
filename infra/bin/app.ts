#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { PortfolioDemosStack } from "../lib/portfolio-demos-stack";

/**
 * CDK App entrypoint.
 *
 * Running `cdk synth` here compiles this TypeScript into a CloudFormation template
 * (see infra/cdk.out/*.template.json). Running `cdk deploy` sends that template to
 * the CloudFormation service, which creates or updates AWS resources.
 */
const app = new cdk.App();

new PortfolioDemosStack(app, "PortfolioDemosStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? "us-east-1",
  },
  description: "Portfolio case-study demos: S3, Secrets Manager, Bedrock Lambda, HTTP API",
});
