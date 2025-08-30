#!/usr/bin/env python3
import asyncio
import os
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession

async def run_demo():
    # Use stdio client instead of HTTP for proper MCP communication
    async with stdio_client("python", "-m", "server.mcp_server", "stdio") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Simulate a battle
            battle_result = await session.call_tool(
                "simulate_battle_tool", 
                arguments={
                    "npc_a": "embermage", 
                    "npc_b": "windblade", 
                    "level": 50, 
                    "seed": 123
                }
            )
            
            battle_data = json.loads(battle_result.content[0].text)
            print("Winner:", battle_data["winner"])
            print("Battle log (first 10 lines):")
            for line in battle_data["log"][:10]:
                print("  ", line)
            
            # Optional narration
            try:
                narration_result = await session.call_tool(
                    "narrate_battle_with_groq", 
                    arguments={
                        "battle_log": battle_data["log"],
                        "style": "sportscaster"
                    }
                )
                narration_data = json.loads(narration_result.content[0].text)
                print("\nNarration:\n", narration_data.get("narration", "")[:500])
            except Exception as e:
                print("Groq narration failed (check GROQ_API_KEY):", e)

if __name__ == "__main__":
    asyncio.run(run_demo())