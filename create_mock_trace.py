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
