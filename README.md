# AI-Powered NPC Battle Arena (Full)
Complete MCP-based demo project for showcasing Model Context Protocol, autonomous NPC agents, and conversational analytics.

## Overview
This project implements:
- MCP server (FastMCP) exposing NPC resources and battle simulation tools
- A turn-based battle engine with 3+ status effects (Burn, Poison, Stun)
- Optional Groq-powered narration (requires GROQ_API_KEY)
- A simple Streamlit dashboard to run simulations and view logs
- Demo client showing how to call MCP tools via streamable HTTP

## Setup (VS Code)
1. Clone and open in VS Code.
2. Create and activate a virtual environment:
```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows (powershell)
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```
3. Create a `.env` file with your Groq key OR run the helper script:
```bash
python scripts/set_env.py --key <YOUR_GROQ_KEY>
```
4. Start the MCP server (Streamable HTTP):
```bash
python server/mcp_server.py http --host 127.0.0.1 --port 8000
```
5. Run demo client to test:
```bash
python client/demo_client.py
```
6. Run Streamlit dashboard (optional):
```bash
streamlit run dashboard/app.py
```

## Files
- `server/` — MCP server, battle engine, Groq client, data.
- `client/` — Demo client using MCP streamable HTTP client.
- `dashboard/` — Minimal Streamlit UI to run matches and view logs.
- `scripts/set_env.py` — Helper to write .env locally with your key (do not commit).
