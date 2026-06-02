import * as cdk from "aws-cdk-lib";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";
import { join } from "path";

const LAMBDA_SRC = join(__dirname, "../../lambdas");

/**
 * PortfolioDemosStack — minimal AWS footprint for portfolio Bedrock demos.
 *
 * HOW CDK RELATES TO CLOUDFORMATION
 * ---------------------------------
 * Each `new Xxx(this, 'Id', { ... })` becomes one or more CloudFormation resources.
 * `cdk synth` prints the template; `cdk deploy` creates a **stack** (unit of deployment).
 * CloudFormation tracks state, rolls back on failure, and shows events in the console.
 */
export class PortfolioDemosStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // --- S3: versioned bucket for generated workbook docs / migration packages ---
    const docsBucket = new s3.Bucket(this, "PortfolioDocs", {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // --- Secrets Manager: shell only — YOU set the JSON value after deploy (no keys in git) ---
    const appSecret = new secretsmanager.Secret(this, "PortfolioDemoConfig", {
      description: "Portfolio demos config (bedrock_model_id, docs_bucket). Set via CLI after deploy.",
      secretStringValue: cdk.SecretValue.unsafePlainText(
        JSON.stringify({
          bedrock_model_id: "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
          note: "Replace docs_bucket after deploy using stack output DocsBucketName",
        })
      ),
    });

    // --- Lambda: Tableau metadata → Bedrock draft/refine → S3 ---
    const tableauDocFn = new lambda.Function(this, "TableauDocGenerator", {
      description: "Generate workbook documentation via Amazon Bedrock Converse",
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "tableau_doc.handler.handler",
      // Asset = lambdas/ folder (tableau_doc + shared/portfolio_aws). For production,
      // add Docker bundling to pip install deps; locally `pip install -t lambdas/` works too.
      code: lambda.Code.fromAsset(LAMBDA_SRC),
      timeout: cdk.Duration.minutes(2),
      memorySize: 512,
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        PORTFOLIO_SECRET_ARN: appSecret.secretArn,
        PORTFOLIO_DOCS_BUCKET: docsBucket.bucketName,
      },
    });

    appSecret.grantRead(tableauDocFn);
    docsBucket.grantReadWrite(tableauDocFn);
    tableauDocFn.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["bedrock:InvokeModel", "bedrock:Converse"],
        resources: ["*"],
      })
    );

    // --- API Gateway HTTP API → Lambda (teaching: integration + route) ---
    const httpApi = new apigwv2.HttpApi(this, "PortfolioDemoApi", {
      apiName: "portfolio-demos",
      description: "Invoke Tableau doc generator (POST /generate with metadata JSON body)",
    });

    httpApi.addRoutes({
      path: "/generate",
      methods: [apigwv2.HttpMethod.POST],
      integration: new integrations.HttpLambdaIntegration("TableauDocIntegration", tableauDocFn),
    });

    // --- Outputs (exported as CloudFormation Outputs — copy into .env locally) ---
    new cdk.CfnOutput(this, "DocsBucketName", {
      value: docsBucket.bucketName,
      description: "S3 bucket for generated documentation",
    });
    new cdk.CfnOutput(this, "SecretArn", {
      value: appSecret.secretArn,
      exportName: "PortfolioDemosSecretArn",
    });
    new cdk.CfnOutput(this, "TableauDocFunctionArn", {
      value: tableauDocFn.functionArn,
    });
    new cdk.CfnOutput(this, "ApiUrl", {
      value: httpApi.apiEndpoint,
      description: "POST {ApiUrl}/generate with metadata JSON",
    });
  }
}
