"""Shared AWS utilities for portfolio demo apps (no secrets in code)."""

from portfolio_aws.bedrock import BedrockConverse
from portfolio_aws.config import DemoConfig, load_config
from portfolio_aws.secrets import get_secret_json

__all__ = ["BedrockConverse", "DemoConfig", "load_config", "get_secret_json"]
