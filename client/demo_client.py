#!/usr/bin/env python3
import asyncio, os
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

async def run_demo():
    async with streamablehttp_client(URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as sess:
            await sess.initialize()
            tools = await sess.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            res = await sess.call_tool("simulate_battle_tool", arguments={"npc_a":"EmberMage", "npc_b":"IronKnight", "level":50, "seed":123})
            out = res.structuredContent
            print("Winner:", out["winner"])
            print("Battle log (first 20 lines):")
            for line in out["log"][:20]:
                print(" ", line[:200])
            # Optional narration
            try:
                narr = await sess.call_tool("narrate_battle_with_groq", arguments={"battle_log": out["log"], "style":"sportscaster"})
                print("\nNarration:\n", narr.structuredContent.get("narration","")[:500])
            except Exception as e:
                print("Groq narration failed (check GROQ_API_KEY):", e)

if __name__=="__main__":
    asyncio.run(run_demo())
