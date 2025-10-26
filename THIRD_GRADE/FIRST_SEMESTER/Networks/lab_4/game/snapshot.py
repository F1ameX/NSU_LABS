def snapshot(engine):
    snakes = {pid: [(c.x,c.y) for c in s.cells] for pid,s in engine.snakes.items() if s.alive}
    return {
        "order": engine.state_order,
        "snakes": snakes,
        "food": list(engine.food),
        "scores": dict(engine.scores)
    }