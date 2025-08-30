import requests

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
        "player_team": ["Pikachu", "Charizard", "Blastoise"],
        "opponent_team": ["Bulbasaur", "Gengar", "Dragonite"],
    }
    response = requests.post(url, json=payload)
    print("Battle Simulation:", response.status_code, response.json() if response.ok else response.text)

if __name__ == "__main__":
    print("=== Testing Backend API ===")
    test_root()
    test_health()
    test_battle()
