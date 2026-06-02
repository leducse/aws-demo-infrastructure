"""Amazon Bedrock Converse API — same pattern as scientific-synthesis/synth."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from portfolio_aws.config import DemoConfig, load_config


@dataclass(slots=True)
class BedrockResponse:
    text: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BedrockConverse:
    def __init__(self, config: DemoConfig | None = None) -> None:
        self.config = config or load_config()
        self._client = None

    def _runtime(self):
        if self._client is None:
            import boto3

            self._client = boto3.client("bedrock-runtime", region_name=self.config.aws_region)
        return self._client

    def complete(
        self,
        user: str,
        *,
        system: str = "You are a helpful assistant.",
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> BedrockResponse:
        resp: dict[str, Any] = self._runtime().converse(
            modelId=self.config.bedrock_model_id,
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": user}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )
        text = resp["output"]["message"]["content"][0]["text"]
        usage = resp.get("usage", {})
        return BedrockResponse(
            text=text,
            input_tokens=int(usage.get("inputTokens", 0)),
            output_tokens=int(usage.get("outputTokens", 0)),
        )
