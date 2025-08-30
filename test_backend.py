import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    url = f"{BASE_URL}/"
    response = requests.get(url)
    print("Root Endpoint:", response.status_code, response.json() if response.ok else response.text)

def test_health():
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print("Health Check:", response.status_code, response.json() if response.ok else response.text)

def test_battle():
    url = f"{BASE_URL}/battle/simulate"
    payload = {
        "npc_a": "embermage",
        "npc_b": "windblade",
        "level": 50,
        "seed": 123,
        "max_turns": 100
    }
    response = requests.post(url, json=payload)
    print("Battle Simulation:", response.status_code)
    if response.ok:
        result = response.json()
        print(f"Winner: {result['winner']}")
        print(f"Turns: {result['turns']}")
        print("First 5 log entries:")
        for line in result['log'][:5]:
            print(f"  {line}")
    else:
        print("Error:", response.text)

def test_ai_query():
    url = f"{BASE_URL}/ai/query"
    payload = {"question": "What is the best strategy for a fire-type NPC?"}
    response = requests.post(url, json=payload)
    print("AI Query:", response.status_code, response.json() if response.ok else response.text)

if __name__ == "__main__":
    print("=== Testing Backend API ===")
    test_root()
    test_health()
    test_battle()
    test_ai_query()