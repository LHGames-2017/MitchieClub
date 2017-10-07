from flask import Flask, request
from structs import *
import json
import math
import numpy

from solver import AStarSolver

app = Flask(__name__)
upgrade_toggle = 1
has_try_upgrade = 0

def create_action(action_type, target):
    actionContent = ActionContent(action_type, target.__dict__)
    return json.dumps(actionContent.__dict__)

def create_move_action(target):
    return create_action("MoveAction", target)

def create_attack_action(target):
    return create_action("AttackAction", target)

def create_collect_action(target):
    return create_action("CollectAction", target)

def create_steal_action(target):
    return create_action("StealAction", target)

def create_heal_action():
    return create_action("HealAction", "")

def create_purchase_action(item):
    return create_action("PurchaseAction", item)

def create_upgrade_action(type):
    actionContent = ActionContent("UpgradeAction", type)
    return json.dumps(actionContent.__dict__)

def deserialize_map(serialized_map):
    """
    Fonction utilitaire pour comprendre la map
    """
    serialized_map = serialized_map[1:]
    rows = serialized_map.split('[')
    column = rows[0].split('{')
    deserialized_map = [[Tile() for x in range(20)] for y in range(20)]
    for i in range(len(rows) - 1):
        column = rows[i + 1].split('{')

        for j in range(len(column) - 1):
            infos = column[j + 1].split(',')
            end_index = infos[2].find('}')
            content = int(infos[0])
            x = int(infos[1])
            y = int(infos[2][:end_index])
            deserialized_map[i][j] = Tile(content, x, y)

    return deserialized_map

def backpack_is_full(player) :
    return (player.CarriedRessources >= player.CarryingCapacity)

def is_tile_ok(tile) :
    return tile.Content == TileContent.Empty

def go_to_tile(player, map, tile):
    """ compute path and return next action to take in the path """
    start = (player.Position.X, player.Position.Y)
    goal = (tile.X, tile.Y)

    if tile.Content != TileType.Tile:
        # goal is 1 away from the tile
        print('Goal is not empty, check surroundings')
        min_d = 9999
        goal = (player.Position.X, player.Position.Y)
        for x, y in [(tile.X-1, tile.Y), (tile.X+1,tile.Y), (tile.X,tile.Y-1), (tile.X,tile.Y+1)]:
            distance = player.Position.Distance(Point(tile.X, tile.Y))
            if distance < min_d:
                min_d = distance
                goal = (x,y)

    print('Start: {}'.format(start))
    print('Goal: {}'.format(goal))
    path = AStarSolver(map).astar(start, goal)
    if path:
        print('Found solution!')
        point = Point(path()[0][0], path()[0][1])
    else:
        print('No solution :(')
        point = Point(start[0], start[1])

    action = create_move_action(point)
    return action

def is_resource(tile) :
    return tile.Content == TileContent.Resource

def find_closest_resource_dumb(player, map) :
    """
    radius = 3
    angle = 1
    while not is_resource(map[target.X][target.Y]) :
        step = angle % radius
        cote = int(angle / radius)
        if cote == 0 :
            target = Point(player.Position+radius-2, )
        elif cote == 1:

        elif cote == 2:

        elif cote == 3:

        radius = radius + 1
    """
    target = None
    min_distance = 1000
    for i in range(len(map)) :
        for j in range(len(map[0])) :
            if is_resource(map[i][j]):
                distance = player.Position.Distance(Point(map[i][j].X, map[i][j].Y))
                if(distance < min_distance) :
                    min_distance = distance
                    target = map[i][j]
    return target

def upgrade_dumb() :
    global upgrade_toggle
    if (upgrade_toggle) :
        upgrade_toggle = 0
        return create_upgrade_action(UpgradeType.CarryingCapacity)
    else :
        upgrade_toggle = 1
        return create_upgrade_action(UpgradeType.CollectingSpeed)


def collect_resource(player, target):
    return create_collect_action(target)

def can_collect_resource(player, target) :
    return player.Position.Distance(target) == 1

def print_map(grid):
    for i in range(len(grid)):
        line = ""
        for j in range(len(grid[0])):
            line += " "
            line += str(grid[i][j].Content) + "-(" + str(grid[i][j].X) + "," + str(grid[i][j].Y) + ")"
        print(line)

def bot():
    """
    Main de votre bot.
    """
    global upgrade_toggle
    global has_try_upgrade
    map_json = request.form["map"]

    # Player info

    encoded_map = map_json.encode()
    map_json = json.loads(encoded_map)
    p = map_json["Player"]
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]
    house = p["HouseLocation"]
    player = Player(p["Health"], p["MaxHealth"], Point(x,y),
                    Point(house["X"], house["Y"]), 0,
                    p["CarriedResources"], p["CarryingCapacity"])

    # Map
    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)

    otherPlayers = []

    for player_dict in map_json["OtherPlayers"]:
        for player_name in player_dict.keys():
            player_info = player_dict[player_name]
            if player_info == 'notAPlayer':
                continue
            p_pos = player_info["Position"]
            player_info = PlayerInfo(player_info["Health"],
                                     player_info["MaxHealth"],
                                     Point(p_pos["X"], p_pos["Y"]))

            otherPlayers.append({player_name: player_info })

    print_map(deserialized_map)

    action = create_move_action(Point(x,y)) # default
    if player.Position.Distance(player.HouseLocation) == 0 :
        # Try to upgrade collecting speed or carrying capacity
        if not has_try_upgrade :
            action = upgrade_dumb()
            has_try_upgrade = 1
        else :
            # find closest resource
            closest_resource = find_closest_resource_dumb(player, deserialized_map)
            # go to resource
            action = go_to_tile(player, deserialized_map, closest_resource)
            has_try_upgrade = 0
    elif backpack_is_full(player) :
        # Return to home
        action = go_to_tile(player, deserialized_map, player.HouseLocation)
    #elif can_collect_resource(player, find_closest_resource_dumb(deserialized_map)):
        # collect resource
    #    action = collect_resource(player)
    else:
        # find closest resource
        closest_resource = find_closest_resource_dumb(player, map)
        if can_collect_resource(player, closest_resource):
            action = collect_resource(player)
        else:
            # go to resource
            action = go_to_tile(player, deserialized_map, closest_resource)

    return action

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
