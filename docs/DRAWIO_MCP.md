# Draw.io MCP — setup for portfolio architecture diagrams

Official server: [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp) · Hosted endpoint: `https://mcp.draw.io/mcp`

## Cursor configuration

Add to your Cursor MCP config (`~/.cursor/mcp.json` under `mcpServers`):

```json
"drawio": {
  "url": "https://mcp.draw.io/mcp"
}
```

Then **Settings → MCP → Refresh** the `drawio` server.

### Alternative: local tool server (opens browser)

```json
"drawio-local": {
  "command": "npx",
  "args": ["-y", "@drawio/mcp"]
}
```

## Recommended workflow for this portfolio

1. **`search_shapes`** — e.g. `"AWS Lambda"`, `"Amazon S3"`, `"Amazon API Gateway"` to get exact style strings.
2. **`create_diagram`** — pass draw.io XML using [xml-reference.md](https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md).
3. Save exports under `docs/architecture/<project>.drawio` and PNG for the consulting site.

### Example prompt in Cursor

> Use drawio to create an AWS architecture diagram for the PortfolioDemos CDK stack:
> API Gateway → Lambda → Bedrock + Secrets Manager + S3. Use search_shapes for AWS icons.
> Save the XML description so I can export to `portfolio-aws-demos/docs/architecture/`.

## Four modes (from draw.io repo)

| Mode | When to use |
|------|-------------|
| **Hosted MCP App** (`mcp.draw.io`) | Inline preview in chat — easiest in Cursor |
| **`npx @drawio/mcp`** | Open diagram in draw.io desktop/web editor |
| **Skill + CLI** | Commit `.drawio` files in git |
| **Project instructions** | Claude Projects without MCP |

For **AWS-shaped** diagrams, prefer draw.io over Mermaid-only tools — `search_shapes` includes AWS/Azure/GCP libraries.
