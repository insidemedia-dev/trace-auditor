import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Import the model from our ingestion module
from trace_auditor.ingestion import ParsedTrace

# 1. Define the structured output schema
class TraceAuditResult(BaseModel):
    trace_id: str
    issue_category: str = Field(description="E.g., Context Overflow, Prompt Injection, Inference Timeout, Format Error")
    root_cause: str = Field(description="A concise explanation of why the trace failed or lagged.")
    recommended_fix: str = Field(description="Actionable step to prevent this in the future.")
    severity: str = Field(description="Low, Medium, High, or Critical")

class TraceAnalyzer:
    def __init__(self):
        print("Initializing Pydantic AI Agent...")
        # Connects to the local LiteLLM gateway defined in .env
        base_url = os.getenv("LLM_BASE_URL", "http://litellm.default.svc.cluster.local:4000/v1")
        model_name = os.getenv("LLM_MODEL", "openai:hosted-sglang-model")
        
        self.agent = Agent(
            model_name,
            model_settings={'base_url': base_url},
            output_type=TraceAuditResult,
            system_prompt=(
                "You are an expert AI Observability Engineer. Your job is to analyze failed "
                "or slow LLM traces, determine the root cause of the issue, and "
                "provide a structured, actionable audit report."
            )
        )

    def analyze_trace(self, trace: ParsedTrace) -> TraceAuditResult:
        """Passes a single parsed trace to the LLM for analysis."""
        print(f"Analyzing trace: {trace.trace_id}...")
        
        prompt = (
            f"Please analyze the following trace data:\n"
            f"Trace ID: {trace.trace_id}\n"
            f"Timestamp: {trace.timestamp}\n"
            f"Latency: {trace.latency_ms}ms\n"
            f"Tags: {trace.tags}\n"
            f"Input Data:\n{trace.input_data}\n\n"
            f"Output Data:\n{trace.output_data}\n"
        )
        
        # run_sync executes the call and forces the output into the TraceAuditResult schema
        result = self.agent.run_sync(prompt)
        return result.data
