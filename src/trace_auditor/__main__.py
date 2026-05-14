import sys
from dotenv import load_dotenv
from trace_auditor.ingestion import TraceIngestionClient

def main():
    # Load variables from .env file for local development
    load_dotenv()
    
    print("Starting Autonomous Trace Auditor...")
    
    # Initialize our new ingestion client
    ingestion_client = TraceIngestionClient()
    
    # Execute the fetch
    bad_traces = ingestion_client.fetch_problematic_traces(minutes_back=60)
    
    if not bad_traces:
        print("Audit complete: Cluster LLM traffic is healthy.")
        sys.exit(0)
        
    print(f"\n--- AUDIT REQUIRED: Found {len(bad_traces)} issues ---")
    for trace in bad_traces:
        print(f"Trace ID: {trace.trace_id} | Latency: {trace.latency_ms:.2f}ms | Tags: {trace.tags}")
    
    print("\n(Milestone 3 will hand these off to Pydantic AI for analysis...)")

if __name__ == "__main__":
    main()
