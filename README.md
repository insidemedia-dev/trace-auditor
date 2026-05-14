# Autonomous Trace Auditor

The Autonomous Trace Auditor is a lightweight, transient Kubernetes CronJob that acts as an automated QA engineer for local LLM traffic. It periodically fetches recent error and latency traces from Langfuse, analyzes them using Pydantic AI routed through the LiteLLM gateway, and outputs structured JSON audit logs containing root cause analysis and recommended fixes.

## Architecture

- **Runtime**: Python 3.12+ 
- **Analysis Framework**: Pydantic AI
- **LLM Gateway**: LiteLLM (Internal)
- **Trace Source**: Langfuse Python SDK
- **Scheduling**: Kubernetes CronJob (runs every 15 minutes)
- **Memory Footprint**: < 256Mi

## Local Development Setup

1. **Install Dependencies**:
   This project uses `pyproject.toml`. You can install the dependencies using `pip` or `uv`:
   ```bash
   pip install -e .
   ```

2. **Configure Environment Variables**:
   Copy the example environment file and fill in your credentials.
   ```bash
   cp .env.example .env
   ```
   You will need:
   - `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
   - `LITELLM_API_KEY`, `LITELLM_API_BASE`
   - `LITELLM_MODEL` (e.g., `openai-chat:gpt-4o` or internal equivalent)

3. **Run Locally**:
   To test the script locally before deploying:
   ```bash
   python -m src.main
   ```

## Cluster Deployment (dss-k3s-01)

This project is deployed directly to the K3s cluster. The container image is built locally on the node and imported into the K3s containerd runtime.

### 1. Build and Import the Image

Build the Docker image locally and import it into K3s:

```bash
# Build the image
docker build -t trace-auditor:latest .

# Export and import into k3s containerd
docker save trace-auditor:latest | sudo k3s ctr images import -
```

### 2. Deploy Secrets

Ensure your `.env` file is populated, then use the provided script to generate and apply the Kubernetes secret:

```bash
./deploy_secrets.sh
```
*(Alternatively, you can manually apply `manifests/secrets.yaml` after encoding your values to base64).*

### 3. Deploy the CronJob

Apply the CronJob manifest to schedule the trace auditor:

```bash
kubectl apply -f manifests/cronjob.yaml
```

To test the CronJob immediately outside of its regular schedule:

```bash
kubectl create job --from=cronjob/trace-auditor trace-auditor-manual-01
kubectl logs -f job/trace-auditor-manual-01
```

## Troubleshooting

For operational issues, failure modes, and debugging steps, please refer to the [Runbook](docs/RUNBOOK.md).
