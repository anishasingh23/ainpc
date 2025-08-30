from server.battle_engine import simulate_battle
def test_simulate():
    out = simulate_battle("embermage","windblade", level=50, seed=1)
    assert "winner" in out
    assert isinstance(out["log"], list)
