"""Model Initialization File

Configures the LLM model used throughout the course.

Default: Anthropic claude-haiku-4-5 (fast, cheap, great for learning).

═══════════════════════════════════════════════════════════════════════════
  ⚠  IMPORTANT: install the matching extra BEFORE swapping providers
═══════════════════════════════════════════════════════════════════════════

  Provider              Install command              Already installed?
  --------------------  ---------------------------  ---------------------
  Anthropic (default)   -                            yes (default dep)
  OpenAI                -                            yes (default dep)
  Azure OpenAI          uv sync --extra azure        no - install first
  AWS Bedrock           uv sync --extra bedrock      no - install first
  Google Vertex/Gemini  uv sync --extra google       no - install first

═══════════════════════════════════════════════════════════════════════════

To swap providers:
  1. Run the install command above (if needed).
  2. Comment out the active model line(s) below.
  3. Uncomment the section for your desired provider.
  4. Set the provider's env vars in `.env` (see notes inline).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)

from langchain.chat_models import init_chat_model


def _init_bedrock_model(
    model_env_var: str, fallback_model_id: str, *, use_default_model_id: bool = True
):
    from langchain_aws import ChatBedrockConverse

    region_name = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    model_id = os.getenv(model_env_var)
    if not model_id and use_default_model_id:
        model_id = os.getenv("BEDROCK_MODEL_ID")
    model_id = model_id or fallback_model_id
    return ChatBedrockConverse(model_id=model_id, region_name=region_name)

# ═══ Default Models ══════════════════════════════════════════════════════════
# Workshop default: Anthropic claude-haiku-4-5, fast and cost-effective.
# Requires ANTHROPIC_API_KEY in .env.
#
# To switch the whole repo to OpenAI without editing lesson files, set:
#   LCA_MODEL_PROVIDER=openai
#   OPENAI_MODEL_ID=gpt-5.5
#   OPENAI_STRONG_MODEL_ID=gpt-5.5
#
# To switch the whole repo to AWS Bedrock without editing lesson files, set:
#   LCA_MODEL_PROVIDER=bedrock
#   AWS_REGION=...
#   BEDROCK_MODEL_ID=anthropic.claude-3-5-haiku-20241022-v1:0
#   BEDROCK_STRONG_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
provider = os.getenv("LCA_MODEL_PROVIDER", "").lower()

if provider == "bedrock":
    model = _init_bedrock_model(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0"
    )
    strong_model = _init_bedrock_model(
        "BEDROCK_STRONG_MODEL_ID",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        use_default_model_id=False,
    )
elif provider == "openai":
    openai_model_id = os.getenv("OPENAI_MODEL_ID", "gpt-5.5")
    openai_strong_model_id = os.getenv("OPENAI_STRONG_MODEL_ID", openai_model_id)
    model = init_chat_model(f"openai:{openai_model_id}", timeout=60, max_retries=2)
    strong_model = init_chat_model(
        f"openai:{openai_strong_model_id}", timeout=120, max_retries=2
    )
else:
    model = init_chat_model("anthropic:claude-haiku-4-5", timeout=60, max_retries=2)

    # A more capable model for steps that need stronger reasoning
    strong_model = init_chat_model("anthropic:claude-sonnet-4-6", timeout=120, max_retries=2)

# ═══ Alternative Models (comment out default above, uncomment one below) ═════
# model = init_chat_model("anthropic:claude-sonnet-4-6")
# model = init_chat_model("openai:gpt-4.1-mini")
# model = init_chat_model("openai:gpt-4.1")
# strong_model = init_chat_model("openai:gpt-4.1")

# ═══ Open-Source / Alternative Hosted Models ══════════════════════════════════

# Groq: fast hosted inference for Llama, Mixtral, and others (free tier available)
# Install first:  uv add langchain-groq
# Requires GROQ_API_KEY in .env  (get one at console.groq.com)
#
# model = init_chat_model("groq:llama-3.3-70b-versatile")

# Ollama: run models locally (no API key required)
# langchain-ollama is already installed (default dep)
# Install the Ollama app first: https://ollama.com
# Pull a model first, e.g.:  ollama pull qwen2.5:7b
#
# model = init_chat_model("ollama:qwen2.5:7b")

# Kimi (Moonshot AI): OpenAI-compatible hosted API
# No extra install needed (langchain-openai is already a default dep)
# Requires KIMI_API_KEY in .env  (get one at platform.moonshot.cn)
#
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="moonshot-v1-8k", base_url="https://api.moonshot.cn/v1", api_key=os.environ["KIMI_API_KEY"])

# OpenRouter: hosted open-source models via OpenAI-compatible API
# No extra install needed (langchain-openai is already a default dep)
# Free models available; sign up at openrouter.ai and get an API key
# Requires OPENROUTER_API_KEY in .env
#
# from langchain_openai import ChatOpenAI
# model = ChatOpenAI(model="nvidia/nemotron-3-ultra-550b-a55b:free", base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])


# ═══ Cloud Provider Models (extra install required, see table above) ═════════
# ─── Azure OpenAI ─────────────────────────────────────────────────────────────
# Install first:  uv sync --extra azure
# Requires AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION in .env
# Set your deployment name directly below (it isn't read from .env)
#
# from langchain_openai import AzureChatOpenAI
# model = AzureChatOpenAI(azure_deployment="gpt-4.1", api_version="2024-12-01-preview")


# ─── AWS Bedrock ──────────────────────────────────────────────────────────────
# Install first:  uv sync --extra bedrock
# Requires standard AWS SDK credentials (env vars, shared config, or OIDC in CI)
# and AWS_REGION / AWS_DEFAULT_REGION.
#
# from langchain_aws import ChatBedrockConverse
# model = ChatBedrockConverse(
#     model_id="anthropic.claude-3-5-haiku-20241022-v1:0",
#     region_name=os.environ["AWS_REGION"],
# )


# ─── Google Gemini ────────────────────────────────────────────────────────────
# Install first:  uv sync --extra google
# Requires GOOGLE_API_KEY in .env
#
# model = init_chat_model("google_genai:gemini-2.5-flash")
