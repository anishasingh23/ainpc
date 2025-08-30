# server/mcp_server.py
import os
import argparse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import uvicorn

# Patch logging for Uvicorn bug on Python 3.11
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


load_dotenv()

from server.battle_engine import simulate_battle
from server.groq_client import query_groq
from server.models import BattleRequest, BattleResponse, BattleAction

app = FastAPI(title="AI NPC Battle Arena")

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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["http"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    # Custom logging config — avoids double logs & %d bug
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
            # Disable FastAPI's internal logger duplication
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
