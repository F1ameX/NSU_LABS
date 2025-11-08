from snakes_proto import snakes_pb2 as pb

def _points_to_cells(points, width=None, height=None):
    if not points:
        return []
    cells = [(points[0].x, points[0].y)]
    for i in range(1, len(points)):
        px, py = cells[-1]
        nx = px + points[i].x
        ny = py + points[i].y
        if width is not None and height is not None:
            nx %= width
            ny %= height
        cells.append((nx, ny))
    return cells

def from_proto_state(state_pb, width, height):
    snakes = {}
    for s in state_pb.snakes:
        # Если когда-нибудь добавим ZOMBIE — тут можно будет учитывать состояние
        cells = _points_to_cells(s.points, width, height)
        snakes[s.player_id] = cells

    # ДЕДУПЛИКАЦИЯ еды: в сет превращаем и обратно в список
    food_set = {(c.x, c.y) for c in state_pb.foods}
    food = list(food_set)

    scores = {}
    names = {}
    for gp in state_pb.players.players:
        scores[gp.id] = gp.score
        names[gp.id] = gp.name
    return {
        "order": state_pb.state_order,
        "snakes": snakes,
        "food": food,
        "scores": scores,
        "names": names,
    }

def to_proto_state(engine, players_list):
    st = pb.GameState()
    st.state_order = getattr(engine, "state_order", 0)

    # ВАЖНО: отправляем ТОЛЬКО живые змейки — чтобы UI корректно включал экран смерти
    for pid, s in engine.snakes.items():
        if not getattr(s, "alive", False):
            continue
        snake_pb = pb.GameState.Snake()
        snake_pb.player_id = pid
        pts = []
        if s.cells:
            pts.append(pb.GameState.Coord(x=s.cells[0].x, y=s.cells[0].y))
            for i in range(1, len(s.cells)):
                dx = s.cells[i].x - s.cells[i - 1].x
                dy = s.cells[i].y - s.cells[i - 1].y
                pts.append(pb.GameState.Coord(x=dx, y=dy))
        snake_pb.points.extend(pts)
        snake_pb.state = pb.GameState.Snake.ALIVE  # ZOMBIE добавим при доработке ролей
        dir_map = {0: pb.UP, 1: pb.DOWN, 2: pb.LEFT, 3: pb.RIGHT}
        snake_pb.head_direction = dir_map.get(getattr(s, "dir", 0), pb.UP)
        st.snakes.append(snake_pb)

    # Еда уже хранится множеством в движке, но на всякий случай не добавляем дубликаты
    food_seen = set()
    for x, y in getattr(engine, "food", []):
        if (x, y) in food_seen:
            continue
        st.foods.append(pb.GameState.Coord(x=x, y=y))
        food_seen.add((x, y))

    gps = pb.GamePlayers()
    for p in players_list:
        gp = pb.GamePlayer()
        gp.name = p.name
        gp.id = p.id
        gp.role = p.role
        gp.type = getattr(p, "type", pb.HUMAN)
        gp.score = getattr(engine, "scores", {}).get(p.id, p.score)
        gps.players.append(gp)
    st.players.CopyFrom(gps)
    return st
