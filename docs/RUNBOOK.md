# Autonomous Trace Auditor Runbook

This runbook covers common failure modes and troubleshooting steps for the Autonomous Trace Auditor Kubernetes CronJob.

## 1. Checking Logs

If you suspect the Trace Auditor is failing, the first step is to check the logs of the most recent job run.

```bash
# Find the latest pod created by the cronjob
kubectl get pods -l app=trace-auditor --sort-by=.metadata.creationTimestamp

# View the logs of the most recent pod
kubectl logs <pod-name>
```

## 2. Common Failure Modes

### LiteLLM Internal Server Error (SGLang Backend Scaled to Zero)

**Symptom**: The Trace Auditor pod logs show a `litellm.InternalServerError` or Pydantic AI raises an exception when attempting to communicate with the model.
**Root Cause**: The underlying SGLang inference backend that LiteLLM routes to has been scaled to zero or is currently unresponsive. The Trace Auditor cannot perform its analysis.
**Resolution**:
1. Check the status of the backend SGLang deployment in the cluster:
   ```bash
   kubectl get pods -n <sglang-namespace>
   ```
2. If the SGLang pods are missing or scaled to zero, scale the deployment back up:
   ```bash
   kubectl scale deployment sglang-backend --replicas=1 -n <sglang-namespace>
   ```
3. Verify that LiteLLM can successfully reach the backend before triggering the trace auditor again.

### Langfuse API Unreachable or Authentication Failure

**Symptom**: Logs indicate connection timeouts, `httpx.ConnectError`, or `AuthenticationError` from the Langfuse SDK.
**Root Cause**: 
- The `LANGFUSE_HOST` is unreachable from within the cluster.
- The Langfuse credentials in the Kubernetes Secret are invalid, expired, or missing.
**Resolution**:
1. Verify the `trace-auditor-secrets` in Kubernetes:
   ```bash
   kubectl get secret trace-auditor-secrets -o yaml
   ```
2. Decode the `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` to ensure they are correct.
3. Test connectivity to the Langfuse host from within the cluster:
   ```bash
   kubectl run curl-test --image=curlimages/curl -it --rm -- sh
   curl -I http://langfuse.dss-k3s-01
   ```

### Memory Limit Exceeded (OOMKilled)

**Symptom**: The pod fails and its status shows `OOMKilled`.
**Root Cause**: The auditor fetched an unusually large trace (e.g., massive context overflow) that exceeded the `256Mi` memory limit when being processed by Pydantic AI.
**Resolution**:
1. Confirm the OOM kill:
   ```bash
   kubectl describe pod <pod-name>
   ```
   Look for `Reason: OOMKilled` under the container state.
2. If this is a persistent issue, temporarily increase the memory limit in `manifests/cronjob.yaml`:
   ```yaml
   resources:
     limits:
       memory: 512Mi
     requests:
       memory: 256Mi
   ```
3. Apply the updated manifest: `kubectl apply -f manifests/cronjob.yaml`.

### No Traces Found

**Symptom**: The pod executes successfully (exit code 0) but outputs no JSON analysis.
**Root Cause**: There were no traces tagged as errors or with high latency in the last 15-minute window.
**Resolution**: This is expected behavior during normal operations. To test if the script is working, you can manually trigger an error trace in Langfuse using a test script (e.g., `create_mock_trace.py`), and then run the auditor manually.
