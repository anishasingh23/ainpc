#!/usr/bin/env python3
"""
Safely write a .env file locally with your GROQ_API_KEY.
Run locally (do NOT paste keys into public places):
python scripts/set_env.py --key <YOUR_GROQ_KEY>
"""
import argparse, os
parser = argparse.ArgumentParser()
parser.add_argument("--key", required=True, help="Your GROQ API key")
parser.add_argument("--model", default="llama3-8b-8192", help="Default Groq model")
args = parser.parse_args()
env_text = f"GROQ_API_KEY={args.key}\nGROQ_MODEL={args.model}\nMCP_HOST=127.0.0.1\nMCP_PORT=8000\n"
with open(".env","w") as f:
    f.write(env_text)
print("Wrote .env in current directory. Keep it secret and do not commit to git.")
