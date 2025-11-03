from proto import snakes_pb2 as pb

def _cells_to_points(cells):
    if not cells:
        return []
    pts = [pb.GameState.Coord(x=cells[0][0], y=cells[0][1])]
    for i in range(1, len(cells)):
        dx = cells[i][0] - cells[i - 1][0]
        dy = cells[i][1] - cells[i - 1][1]
        pts.append(pb.GameState.Coord(x=dx, y=dy))
    return pts

def _points_to_cells(points, width=None, height=None):
    if not points:
        return []
    cells = [(points[0].x, points[0].y)]
    for i in range(1, len(points)):
        px, py = cells[-1]
        nx = px + points[i].x
        ny = py + points[i].y
        if width is not None:
            nx %= width
        if height is not None:
            ny %= height
        cells.append((nx, ny))
    return cells

def to_proto_state(engine, players_pb_list):
    st = pb.GameState()
    st.state_order = engine.state_order
    for pid, s in engine.snakes.items():
        snake = pb.GameState.Snake()
        snake.player_id = pid
        snake.state = pb.GameState.Snake.ALIVE if s.alive else pb.GameState.Snake.ZOMBIE
        snake.head_direction = {0: pb.UP, 1: pb.DOWN, 2: pb.LEFT, 3: pb.RIGHT}[s.dir]
        cells = [(c.x, c.y) for c in s.cells]
        snake.points.extend(_cells_to_points(cells))
        st.snakes.append(snake)
    for (x, y) in engine.food:
        st.foods.append(pb.GameState.Coord(x=x, y=y))
    st.players.players.extend(players_pb_list)
    return st

def from_proto_state(state_pb, width: int, height: int):
    snakes = {}
    for s in state_pb.snakes:
        cells = _points_to_cells(s.points, width=width, height=height)
        snakes[s.player_id] = cells
    food = [(c.x % width, c.y % height) for c in state_pb.foods]
    scores = {p.id: p.score for p in state_pb.players.players}
    names = {p.id: p.name for p in state_pb.players.players}
    return {
        "order": state_pb.state_order,
        "snakes": snakes,
        "food": food,
        "scores": scores,
        "names": names,  # <— NEW
    }

def local_snapshot(engine):
    snakes = {
        pid: [(c.x, c.y) for c in s.cells]
        for pid, s in engine.snakes.items() if s.alive
    }
    return {
        "order": engine.state_order,
        "snakes": snakes,
        "food": list(engine.food),
        "scores": dict(engine.scores),
    }