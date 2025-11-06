#!/usr/bin/env python
"""
Simple test script for JD Classifier
Tests the agent without needing full Docker infrastructure
"""
import asyncio
import json
import os
from laddr import AgentRunner, LaddrConfig

# Test cases
TEST_CASES = [
    {
        "name": "Espresso Recipe",
        "input": {
            "query": "I want to file notes about my espresso brewing technique, including grind settings and timing"
        }
    },
    {
        "name": "Work Meeting Today",
        "input": {
            "query": "Notes from today's client meeting about the audio engineering project"
        }
    },
    {
        "name": "Vim Configuration",
        "input": {
            "query": "My custom vim configuration and keybindings"
        }
    },
    {
        "name": "Birthday Memory",
        "input": {
            "query": "Photos and memories from my 25th birthday party"
        }
    },
    {
        "name": "React Learning",
        "input": {
            "query": "Notes from a React tutorial I'm following on Udemy"
        }
    }
]


async def test_agent(test_case):
    """Run a single test case"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_case['name']}")
    print(f"{'='*60}")
    print(f"Query: {test_case['input']['query']}\n")

    try:
        runner = AgentRunner(env_config=LaddrConfig())
        result = await runner.run(
            test_case["input"],
            agent_name="jd_classifier"
        )

        if result.get("status") == "success":
            print("✅ SUCCESS")
            print(f"\nResult:\n{result.get('result', 'No result')}\n")
        else:
            print("❌ FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return {"status": "error", "error": str(e)}


async def main():
    """Run all test cases"""
    print("\n" + "="*60)
    print("STRWBRRY JD CLASSIFIER TEST SUITE")
    print("="*60)

    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("\n⚠️  WARNING: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenRouter API key to run these tests.")
        print("Get your key at: https://openrouter.ai/keys\n")
        return

    print(f"\nLLM Backend: {os.getenv('LLM_BACKEND', 'openai')}")
    print(f"Model: {os.getenv('LLM_MODEL', 'anthropic/claude-3.5-sonnet')}")
    print(f"Base URL: {os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')}")

    results = []
    for test_case in TEST_CASES:
        result = await test_agent(test_case)
        results.append({
            "name": test_case["name"],
            "status": result.get("status"),
            "result": result
        })

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"Passed: {success_count}/{len(results)}")

    if success_count == len(results):
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
