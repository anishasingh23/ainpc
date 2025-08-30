# server/mcp_server.py
import os
import argparse
import logging
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# MCP imports
from mcp.server import Server
from mcp.server.fastapi import create_app
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Local imports (use relative imports)
from .battle_engine import simulate_battle
from .groq_client import query_groq
from .models import BattleRequest, BattleResponse, BattleAction

# Patch logging for Uvicorn bug on Python 3.11
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
load_dotenv()

# Create MCP Server
mcp_server = Server("ai-npc-battle-arena")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for MCP clients."""
    return [
        Tool(
            name="simulate_battle_tool",
            description="Simulate a battle between two NPCs",
            inputSchema={
                "type": "object",
                "properties": {
                    "npc_a": {"type": "string", "description": "First NPC key"},
                    "npc_b": {"type": "string", "description": "Second NPC key"},
                    "level": {"type": "integer", "description": "NPC level", "default": 50},
                    "seed": {"type": "integer", "description": "Random seed for reproducibility"},
                    "max_turns": {"type": "integer", "description": "Maximum turns", "default": 200}
                },
                "required": ["npc_a", "npc_b"]
            }
        ),
        Tool(
            name="narrate_battle_with_groq",
            description="Narrate a battle log using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "battle_log": {"type": "array", "items": {"type": "string"}, "description": "Battle log lines"},
                    "style": {"type": "string", "description": "Narration style", "default": "neutral"}
                },
                "required": ["battle_log"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from MCP clients."""
    if name == "simulate_battle_tool":
        npc_a = arguments.get("npc_a")
        npc_b = arguments.get("npc_b")
        level = arguments.get("level", 50)
        seed = arguments.get("seed")
        max_turns = arguments.get("max_turns", 200)
        
        result = simulate_battle(npc_a, npc_b, level, seed, max_turns)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "narrate_battle_with_groq":
        battle_log = arguments.get("battle_log", [])
        style = arguments.get("style", "neutral")
        
        prompt = f"Narrate this battle in a {style} style:\n\n" + "\n".join(battle_log[:50])
        narration = query_groq(prompt)
        return [TextContent(type="text", text=json.dumps({"narration": narration}))]
    
    raise ValueError(f"Unknown tool: {name}")

# Create FastAPI app and mount MCP app
app = FastAPI(title="AI NPC Battle Arena")
mcp_app = create_app(mcp_server)
app.mount("/mcp", mcp_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI NPC Battle Arena MCP server running."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI NPC Battle Arena"}

@app.post("/battle/simulate", response_model=BattleResponse)
async def battle_simulate_endpoint(req: BattleRequest):
    try:
        res = simulate_battle(req.npc_a, req.npc_b, level=req.level, seed=req.seed, max_turns=req.max_turns)
        # convert actions dicts to BattleAction models
        actions = [BattleAction(**{
            "turn": a.get("turn"),
            "actor": a.get("actor"),
            "action": a.get("action"),
            "target": a.get("target"),
            "damage": a.get("damage"),
            "status_applied": a.get("status_applied"),
            "actor_hp": a.get("actor_hp"),
            "target_hp": a.get("target_hp"),
        }) for a in res.get("actions", [])]
        return BattleResponse(
            winner=res["winner"],
            turns=res["turns"],
            log=res["log"],
            actions=actions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/query")
async def ai_query_endpoint(question: str):
    try:
        ans = query_groq(question)
        return {"answer": ans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["http", "stdio"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    if args.mode == "stdio":
        # Run as stdio server for MCP clients
        stdio_server(mcp_server)
    else:
        # Run as HTTP server
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": None,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "fastapi": {"handlers": ["default"], "level": "WARNING", "propagate": False},
            },
        }

        uvicorn.run(
            "server.mcp_server:app",
            host=args.host,
            port=args.port,
            reload=False,
            log_config=log_config,
        )

if __name__ == "__main__":
    main()