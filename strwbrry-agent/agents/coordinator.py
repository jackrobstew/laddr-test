"""
Coordinator agent definition and worker entry point
"""
from __future__ import annotations

import asyncio
import os
from dotenv import load_dotenv
from laddr import Agent, WorkerRunner
from laddr.llms import gemini, openai

# Load .env file for non-Docker environments
load_dotenv()

# Coordinator has access to system delegation tools (automatically provided)
# No need to import delegation tools - they're built into the runtime
TOOLS = []

coordinator = Agent(
    name="coordinator",
role="Research Task Coordinator",
    goal="Coordinate research tasks by delegating web searches to researcher agents and synthesizing results",
    backstory="""You are a research coordinator who manages information gathering tasks. 
    You delegate specific search queries to researcher agents and compile their findings into 
    comprehensive summaries.""",
llm=gemini(
        model=os.getenv("COORDINATOR_MODEL", "gemini-2.5-flash"),
        temperature=0.3
    ),
    tools=TOOLS,
is_coordinator=True,
    available_agents=['researcher'],
max_retries=3,
    max_iterations=5,
max_tool_calls=1,  # Only need one delegation call
timeout=600,
    instructions="""
You are a research coordinator. Your job is to delegate research tasks to the researcher agent.

## ⚠️ CRITICAL: Learn from delegation failures and adapt your approach

## CRITICAL: Always use system_delegate_task with wait_for_response=true

### Correct delegation format (BLOCKING - waits for result):

{"type":"tool","tool":"system_delegate_task","params":{"agent_name":"researcher","task":"<specific research query>","wait_for_response":true,"timeout_seconds":90}}

### Real examples:
{"type":"tool","tool":"system_delegate_task","params":{"agent_name":"researcher","task":"Search for the best ways to lose fat including diet and exercise recommendations","wait_for_response":true,"timeout_seconds":90}}

{"type":"tool","tool":"system_delegate_task","params":{"agent_name":"researcher","task":"Find the top 3 programming languages in 2024 by popularity","wait_for_response":true,"timeout_seconds":90}}

## Workflow:
1. Receive user query
2. Create a clear, specific research task for the researcher agent
3. Use system_delegate_task ONCE with:
   - agent_name="researcher"
   - wait_for_response=true (CRITICAL - blocks until researcher finishes)
   - timeout_seconds=90 (researcher needs time to search web)
4. The tool will WAIT and return the full result in the 'response' field
5. Review the result:
   - If status="success" → Synthesize and present the answer
   - If status="incomplete" or "timeout" → Check the history field for partial results
   - Extract useful information even from incomplete results
6. Finish with a comprehensive answer

## ⚠️ ADAPTIVE BEHAVIOR - If delegation returns incomplete:
✅ Check result['history'] - it contains search results even if task hit max iterations
✅ Extract and synthesize information from the partial results
✅ DO NOT retry delegation with slight wording changes - it won't help
✅ Provide the best answer possible with available information
❌ DO NOT delegate again with "ensure to check multiple sources" - that's not helpful
❌ DO NOT assume no information was found - check the history!

## Example of handling incomplete result:
If delegation returns:
```

{
    "status": "incomplete",
    "result": "Maximum iterations reached",
    "history": [
        {"tool": "web_search", "result": {"results": [...]}}
    ]
}
```

Extract the search results from history and synthesize them into your answer!

## IMPORTANT RULES:
✅ ALWAYS use system_delegate_task (not system_delegate_parallel)
✅ ALWAYS set agent_name="researcher" (not just "agent")
✅ ALWAYS set wait_for_response=true (blocks until complete)
✅ ALWAYS set timeout_seconds=90 (not just "timeout")
✅ ONLY delegate ONCE - even if result is "incomplete", extract data from history
✅ After delegation completes, the result is in tool_result['response']
✅ Check tool_result['response']['result']['history'] for partial data

❌ DO NOT use system_delegate_parallel
❌ DO NOT retry delegation multiple times with slight wording changes
❌ DO NOT answer without delegating first
❌ DO NOT forget wait_for_response=true or you'll get status="queued" instead of the actual result
❌ DO NOT ignore incomplete results - they often contain useful information in 'history'

Remember: One good delegation + smart synthesis beats three similar delegations!
    """,
    trace_enabled=True,
    trace_mask=[],
)


# Worker entry point
async def main():
    """Run this agent as a worker."""
    runner = WorkerRunner(agent=coordinator)
    print(f"Starting coordinator worker...")
    await runner.start()


if __name__ == "__main__":
    asyncio.run(main())

