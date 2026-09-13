# Deep Agents

Course materials for the [Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course on LangChain Academy.

## Contents

- **[python/](python/)** — Python implementation. See [python/README.md](python/README.md) for setup instructions.
- **typescript/** — TypeScript implementation (coming soon).
- **[agent-chat-ui/](agent-chat-ui/)** — fork of [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) with additions for lesson 5.5, "The Sales Assistant (Advanced)". Other lessons use the hosted UI instead.

## GitHub Actions Bedrock deployment

The `Deploy Bedrock Agent` workflow runs a Python lesson agent under `python/` against AWS Bedrock.

Configure these repository settings before using it:

- **Variable:** `AWS_ROLE_TO_ASSUME`
- **Optional variables:** `AWS_REGION`, `BEDROCK_MODEL_ID`, `BEDROCK_STRONG_MODEL_ID`, `BEDROCK_AGENT_SCRIPT`
- **Optional secret:** `LANGSMITH_API_KEY`

Updating repository variables or secrets does not trigger the workflow by itself; after changing them, run `Deploy Bedrock Agent` with `workflow_dispatch` (or push a matching code change).
