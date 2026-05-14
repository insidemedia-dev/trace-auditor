#!/bin/bash
export LANGFUSE_SECRET_KEY=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_SECRET_KEY)
export LANGFUSE_PUBLIC_KEY=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_PUBLIC_KEY)
export LANGFUSE_HOST=$(~/bin/secret.sh get dss-k3s-01 LANGFUSE_HOST)

sudo k3s ctr run --rm \
  --env LANGFUSE_SECRET_KEY="$LANGFUSE_SECRET_KEY" \
  --env LANGFUSE_PUBLIC_KEY="$LANGFUSE_PUBLIC_KEY" \
  --env LANGFUSE_HOST="$LANGFUSE_HOST" \
  docker.io/library/trace-auditor:0.1.0 test-mock \
  python -c '
from langfuse import Langfuse
from datetime import datetime

print("Initializing Langfuse client...")
client = Langfuse()

print("Creating mock error trace...")
trace = client.trace(
    name="test-error-trace",
    input={"model": "non-existent-model", "messages": [{"role": "user", "content": "Hello"}]},
    output={"error": "Model not found"},
    tags=["error"],
    start_time=datetime.now(),
    end_time=datetime.now()
)

print("Flushing client...")
client.flush()
print("Done. Trace created.")
'
