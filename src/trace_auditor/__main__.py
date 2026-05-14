import sys
from dotenv import load_dotenv
from trace_auditor.ingestion import TraceIngestionClient
from trace_auditor.analyzer import TraceAnalyzer

def main():
    # Load variables from .env file for local development
    load_dotenv()
    
    print("Starting Autonomous Trace Auditor...")
    
    # Initialize our clients
    ingestion_client = TraceIngestionClient()
    analyzer = TraceAnalyzer()
    
    # Execute the fetch
    bad_traces = ingestion_client.fetch_problematic_traces(minutes_back=60)
    
    if not bad_traces:
        print("Audit complete: Cluster LLM traffic is healthy.")
        sys.exit(0)
        
    print(f"\n--- AUDIT REQUIRED: Found {len(bad_traces)} issues ---")
    
    # Process each trace through the Pydantic AI pipeline
    for trace in bad_traces:
        try:
            audit_result = analyzer.analyze_trace(trace)
            
            # Print the structured output for K8s logging to pick up
            print("\n" + "="*50)
            print(f"TRACE ID: {audit_result.trace_id}")
            print(f"CATEGORY: {audit_result.issue_category} (Severity: {audit_result.severity})")
            print(f"ROOT CAUSE: {audit_result.root_cause}")
            print(f"RECOMMENDED FIX: {audit_result.recommended_fix}")
            print("="*50)
            
        except Exception as e:
            print(f"Failed to analyze trace {trace.trace_id}: {e}")

if __name__ == "__main__":
    main()
