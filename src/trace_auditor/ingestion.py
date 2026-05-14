import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel
from langfuse import Langfuse

# 1. Define our clean internal data structure
class ParsedTrace(BaseModel):
    trace_id: str
    timestamp: datetime
    latency_ms: float
    input_data: str
    output_data: Optional[str] = None
    tags: List[str] = []

class TraceIngestionClient:
    def __init__(self):
        # Automatically picks up LANGFUSE_PUBLIC_KEY, SECRET_KEY, and HOST from environment
        print("Initializing Langfuse client...")
        self.client = Langfuse()

    def fetch_problematic_traces(self, minutes_back: int = 15) -> List[ParsedTrace]:
        """Fetches traces that are tagged with 'error' or have high latency."""
        print(f"Fetching traces from the last {minutes_back} minutes...")
        
        # Calculate our time window
        from_timestamp = datetime.now(timezone.utc) - timedelta(minutes=minutes_back)
        
        parsed_traces = []
        
        try:
            # Fetch traces. We use tags to find explicit errors.
            # In a production environment, you might also query by latency thresholds.
            response = self.client.api.trace.list(
                from_timestamp=from_timestamp,
                limit=50
            )
            
            if not response.data:
                print("No problematic traces found in this window.")
                return parsed_traces
                
            for trace in response.data:
                # Calculate latency
                latency = 0.0
                if trace.timestamp and trace.updated_at:
                    latency = (trace.updated_at - trace.timestamp).total_seconds() * 1000

                parsed_traces.append(
                    ParsedTrace(
                        trace_id=trace.id,
                        timestamp=trace.timestamp,
                        latency_ms=latency,
                        input_data=str(trace.input) if trace.input else "No input recorded",
                        output_data=str(trace.output) if trace.output else "No output recorded",
                        tags=trace.tags or []
                    )
                )
                
            print(f"Successfully ingested and parsed {len(parsed_traces)} problematic traces.")
            return parsed_traces
            
        except Exception as e:
            print(f"Failed to fetch traces from Langfuse: {e}")
            return []
