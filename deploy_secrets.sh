#!/bin/bash
LF_SEC=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_SECRET_KEY)
LF_PUB=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_PUBLIC_KEY)
LF_HOST=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_HOST)
LLM_KEY=$(~/bin/secret.sh get dss-k3s-01 LITELLM_MASTER_KEY)

sudo k3s kubectl create secret generic trace-auditor-secrets \
  --from-literal=LANGFUSE_SECRET_KEY=$LF_SEC \
  --from-literal=LANGFUSE_PUBLIC_KEY=$LF_PUB \
  --from-literal=LANGFUSE_HOST=$LF_HOST \
  --from-literal=LLM_API_KEY=$LLM_KEY \
  --from-literal=LLM_BASE_URL='http://litellm.100.80.0.55.nip.io/v1' \
  --from-literal=LLM_MODEL='openai/Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4' \
  --dry-run=client -o yaml | sudo k3s kubectl apply -f -
