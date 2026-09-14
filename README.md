# Deep Agents

Course materials for the [Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course on LangChain Academy.

## Contents

- **[python/](python/)** — Python implementation. See [python/README.md](python/README.md) for setup instructions.
- **typescript/** — TypeScript implementation (coming soon).
- **[agent-chat-ui/](agent-chat-ui/)** — fork of [langchain-ai/agent-chat-ui](https://github.com/langchain-ai/agent-chat-ui) with additions for lesson 5.5, "The Sales Assistant (Advanced)". Other lessons use the hosted UI instead.

## GitHub Actions agent run

The [`Deploy Bedrock Agent`](.github/workflows/deploy-bedrock-agent.yml) workflow runs a Python lesson agent under `python/`. It defaults to OpenAI GPT-5.5 and can also run against AWS Bedrock when `LCA_MODEL_PROVIDER=bedrock`.
By default it runs `m1/m1.5_homework_filled.py`.
`BEDROCK_AGENT_SCRIPT` (or the manual `script_path` input) must point to an existing `.py` file under `python/`; both `m1/m1.5_homework_filled.py` and `python/m1/m1.5_homework_filled.py` are accepted.

Configure these repository settings before using the default GPT-5.5 path:

| Type | Name | Value |
| --- | --- | --- |
| Secret (required) | `OPENAI_API_KEY` | API key used by `langchain-openai` |
| Variable | `LCA_MODEL_PROVIDER` | Defaults to `openai`; set only if overriding |
| Variable | `OPENAI_MODEL_ID` | Defaults to `gpt-5.5` |
| Variable | `OPENAI_STRONG_MODEL_ID` | Defaults to `OPENAI_MODEL_ID`, then `gpt-5.5` |
| Variable | `BEDROCK_AGENT_SCRIPT` | Fallback script path when the dispatch input is empty |
| Secret | `LANGSMITH_API_KEY` | Needed if LangSmith tracing is enabled |
| Variable | `LANGSMITH_TRACING` | Defaults to `false`; set to `true` to enable tracing |
| Variable | `LANGSMITH_PROJECT` | Defaults to `lca-deepagents` |

Do not set AWS variables for the default OpenAI/GPT-5.5 path. AWS OIDC is only used when `LCA_MODEL_PROVIDER=bedrock`.

### AWS authentication with GitHub OIDC

When `LCA_MODEL_PROVIDER=bedrock`, the workflow uses OpenID Connect (OIDC), not stored AWS access keys. GitHub issues a short-lived identity token, and `aws-actions/configure-aws-credentials` exchanges it through AWS STS for temporary IAM role credentials. The Python agent then uses those credentials automatically.

The workflow already has `id-token: write` (to request the OIDC token), `contents: read` (to check out the repository), and a credential configuration step that only runs for Bedrock. `id-token: write` does not itself grant access to AWS resources; the IAM role's trust and permissions policies control that access.

Configuration validation, OIDC authentication, and an STS identity check run before Python dependencies are installed. The credential action clears pre-existing AWS environment credentials and exports the temporary role credentials for the agent. All JavaScript actions in this workflow use the Node.js 24 runtime.

#### 1. Register GitHub as an IAM identity provider

In the AWS account that will run Bedrock inference, open **IAM > Identity providers > Add provider** and select **OpenID Connect**:

- **Provider URL:** `https://token.actions.githubusercontent.com`
- **Audience:** `sts.amazonaws.com`

Reuse the provider if it already exists in that account.

#### 2. Create the IAM role and trust policy

Create an IAM role for **Web identity**, using the GitHub provider and audience above. For example, name it `github-actions-bedrock`.

Set its trust policy to the following, replacing `123456789012` with your AWS account ID:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:milvi-digital@328824617/lca-deepagents@1368681077:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

This repository uses **immutable OIDC subjects**, so the owner and repository IDs in the `sub` value are required. The older `repo:milvi-digital/lca-deepagents:ref:refs/heads/main` format will not match its current configuration. For a fork or a renamed/transferred repository, use that repository's own subject prefix and IDs. You can inspect the current configuration with:

```bash
gh api repos/milvi-digital/lca-deepagents/actions/oidc/customization/sub
```

The example only permits runs from `main`. Select `main` when dispatching the workflow, and protect that branch. Do not replace the subject with a repository-wide wildcard to work around an authentication failure. If you later add a GitHub environment to the job, update the subject to use `:environment:ENVIRONMENT_NAME` instead of the branch suffix, and configure environment protection rules.

#### 3. Grant Bedrock permissions

Attach a separate permissions policy to the role. The trust policy above only controls who can assume the role; it does not authorize model calls.

For direct invocation of the workflow's default foundation models in `us-east-1`, this is an example scoped policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
      ]
    }
  ]
}
```

Adjust the region and model resources to match your selected models and their availability in your AWS account. Foundation-model ARNs intentionally have an empty account-ID segment. If you use inference profiles instead, also authorize the relevant profile and underlying model resources, including destination regions for cross-region inference, and grant `bedrock:GetInferenceProfile` on the profile. Complete any model-provider access prerequisites separately; successful OIDC authentication alone does not enable access to every model.

#### 4. Configure GitHub and run the workflow

Open **Settings > Secrets and variables > Actions** in this repository:

| Type | Name | Value |
| --- | --- | --- |
| Variable (required) | `AWS_ROLE_TO_ASSUME` | The role ARN, e.g. `arn:aws:iam::123456789012:role/github-actions-bedrock` |
| Variable | `AWS_REGION` | Your Bedrock region; falls back to `AWS_DEFAULT_REGION`, then `us-east-1` |
| Variable | `BEDROCK_MODEL_ID` | Model ID or inference profile used by the agent; defaults to Claude 3.5 Haiku |
| Variable | `BEDROCK_STRONG_MODEL_ID` | Strong-model override; falls back to `BEDROCK_MODEL_ID`, then Claude 3.5 Sonnet |
| Variable | `BEDROCK_AGENT_SCRIPT` | Fallback script path when the dispatch input is empty |
| Secret | `LANGSMITH_API_KEY` | Needed if LangSmith tracing is enabled |
| Variable | `LANGSMITH_TRACING` | Defaults to `false`; set to `true` to enable tracing |
| Variable | `LANGSMITH_PROJECT` | Defaults to `lca-deepagents` |

Do not add `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` secrets for this workflow. The role ARN is configuration, not a secret.

`AWS_ROLE_TO_ASSUME` must contain `arn:aws:iam::<account-id>:role/<role-name>`, **not** `arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com`. The provider ARN belongs in the role's trust policy, not in this repository variable.

Go to **Actions > Deploy Bedrock Agent > Run workflow**, select **main**, and set `script_path` if needed. Its default is `m1/m1.5_homework_filled.py`, which takes precedence over `BEDROCK_AGENT_SCRIPT` unless the input is cleared. Running the agent with Bedrock makes Bedrock model calls and can incur charges; the workflow does not provision an AWS-hosted agent service.

### Authentication troubleshooting

- **`AWS_ROLE_TO_ASSUME must be set`:** Add the repository variable under **Variables**, not **Secrets**; the workflow reads `vars.AWS_ROLE_TO_ASSUME`.
- **`AWS_ROLE_TO_ASSUME contains an OIDC provider ARN`:** Create or choose an IAM role that trusts the provider using the policy above, then replace the variable with the role's ARN. A provider cannot be assumed directly.
- **`Not authorized to perform sts:AssumeRoleWithWebIdentity`:** Check the role ARN, provider account, audience, and exact subject (including immutable IDs and selected branch). An environment or custom subject configuration changes the required match.
- **OIDC token unavailable:** Ensure `id-token: write` remains enabled for the job and that you are running through GitHub Actions, not directly in a local shell.
- **Bedrock `AccessDeniedException` after credentials are configured:** Check the role's model permissions, account-level restrictions, selected region, inference-profile resources, and model access prerequisites. This is distinct from an OIDC trust failure.

The **Verify AWS identity** step runs `aws sts get-caller-identity` immediately after **Configure AWS credentials**. It reports the account and assumed-role ARN without printing credentials. Never log AWS secrets or the raw OIDC token.

### Official documentation

- [GitHub: Configuring OpenID Connect in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [GitHub: Immutable OIDC subject claims](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims)
- [AWS: Create an IAM role for GitHub OIDC](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html#idp_oidc_Create_GitHub)
- [AWS: Bedrock model inference permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-prereq.html)
