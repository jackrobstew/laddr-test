#!/usr/bin/env python
"""
Get insights from the Vault Advisory Council
Runs multiple advisory agents and synthesizes their perspectives
"""
import asyncio
import json
import os
import sys
from laddr import AgentRunner, LaddrConfig
from datetime import datetime


async def get_advisory_report():
    """Run the vault advisor coordinator to get full council report"""
    print("="*70)
    print("STRWBRRY VAULT ADVISORY COUNCIL")
    print("="*70)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("\nInitializing advisory council...")
    print("  - The Skeptic (truth-teller)")
    print("  - The Pattern Seeker (cycle detective)")
    print("  - The Guardian (early warning system)")
    print("\n" + "-"*70)

    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openrouter-api-key-here":
        print("\n⚠️  ERROR: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenRouter API key to run the advisory council.")
        print("Get your key at: https://openrouter.ai/keys\n")
        sys.exit(1)

    # Check if vault path is set
    vault_path = os.getenv("VAULT_PATH")
    if not vault_path:
        print("\n⚠️  WARNING: VAULT_PATH not set")
        print("Set it in .env: VAULT_PATH=/path/to/Documents/SPLN")
        print("Or: export VAULT_PATH=/path/to/Documents/SPLN")
        print("\nWill attempt to find vault in default locations...")

    try:
        print("\nRunning advisory council analysis...")
        print("(This may take 3-10 minutes as all agents analyze your vault)")
        print("\nProgress:")
        print("  1. Vault Advisor coordinates analysis...")
        print("  2. The Skeptic analyzes stated vs actual priorities...")
        print("  3. The Pattern Seeker identifies cycles...")
        print("  4. The Guardian assesses risks...")
        print("  5. Final synthesis and recommendations...")
        print("\n⏳ Please wait - comprehensive analysis in progress...\n")

        runner = AgentRunner(env_config=LaddrConfig())
        result = await runner.run(
            {"query": "Analyze the user's vault and provide comprehensive insights"},
            agent_name="vault_advisor"
        )

        print("\n✅ Analysis complete!\n")
        print("-"*70)

        if result.get("status") == "success":
            print("\n✅ ADVISORY COUNCIL REPORT COMPLETE\n")
            print("="*70)
            report = result.get("result", "No result returned")
            print(report)
            print("="*70)

            # Optionally save to file
            save_choice = input("\n\nSave report to file? (y/n): ")
            if save_choice.lower() == 'y':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"advisory_report_{timestamp}.md"
                with open(filename, 'w') as f:
                    f.write(f"# Vault Advisory Council Report\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    f.write(report)
                print(f"\n✅ Report saved to: {filename}")

        else:
            print("\n❌ ADVISORY COUNCIL FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            if "history" in result:
                print("\nPartial results available in execution history")

        return result

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


async def get_single_advisor(advisor_name: str):
    """Run a single advisor agent"""
    valid_advisors = ["skeptic", "pattern_seeker", "guardian"]

    if advisor_name not in valid_advisors:
        print(f"\n❌ Invalid advisor: {advisor_name}")
        print(f"Valid options: {', '.join(valid_advisors)}")
        return

    advisor_names = {
        "skeptic": "The Skeptic",
        "pattern_seeker": "The Pattern Seeker",
        "guardian": "The Guardian"
    }

    print("="*70)
    print(f"CONSULTING: {advisor_names[advisor_name]}")
    print("="*70)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        print(f"\n{advisor_names[advisor_name]} is analyzing your vault...\n")

        runner = AgentRunner(env_config=LaddrConfig())
        result = await runner.run(
            {"query": "Analyze the user's vault from your unique perspective"},
            agent_name=advisor_name
        )

        if result.get("status") == "success":
            print("\n" + "-"*70)
            print(result.get("result", "No result returned"))
            print("-"*70)
        else:
            print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return {"status": "error", "error": str(e)}


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Single advisor mode
        advisor = sys.argv[1]
        asyncio.run(get_single_advisor(advisor))
    else:
        # Full council mode
        asyncio.run(get_advisory_report())


if __name__ == "__main__":
    main()
