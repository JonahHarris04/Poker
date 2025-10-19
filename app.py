from flask import Flask, request
from flask_socketio import SocketIO, emit

from game import PokerGame

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # allow external connections

# Single game instance
game = PokerGame()

player_counter = 0

# Event handlers

# When someone connects
@socketio.on('connect')
def handle_connect():
    print(f"Player connected: {request.sid}")
    emit('connected', {'message': 'Connected to server!'})


# When a player sets their name
@socketio.on('set_name')
def handle_set_name(data):
    global player_counter
    player_counter += 1 # incrementing the counter each time a player joins
    name = f"Player {player_counter}"

    #name = data.get('player_name', 'Anonymous')
    uuid = request.sid
    game.add_player(name, uuid, seat_position=data.get('seat_position', 0), seat_position_flag=data.get('seat_position_flag', 0))

    print(f"Added player: {name}, SID={uuid}")
    print(f"Current players: {[p.name for p in game.players.values()]}")

    # Notify all players of player list
    emit('player_list', [player.to_dict() for player in game.players.values()], broadcast=True)


# Start a new round
@socketio.on('start_game')
def handle_start_game(_):
    if game.round_active:
        emit('error', {'message': 'A round is already in progress!'})
        return

    if len(game.players) < 2:
        emit('error', {'message': 'You must have at least 2 players!'})
        return

    game.start_round()
    print("New round started")

    # Send each player their hand
    for player in game.players.values():
        emit('hand', {'cards': [str(card) for card in player.hand]}, to=player.uuid)

    # Notify current player it's their turn
    current_player = game.current_player()
    emit('your_turn', {'message': "It's your turn!"}, to=current_player.uuid)


@socketio.on('request_flop')
def handle_flop_request(_):
    if not game.round_active:
        emit('error', {'message': 'No active round.'})
        return

    if len(game.community_cards) > 0:
        return  # Flop already dealt

    game.deal_flop()
    print("Flop dealt:", [str(c) for c in game.community_cards])
    emit('community_update', {'cards': [str(c) for c in game.community_cards]}, broadcast=True)


@socketio.on('request_turn')
def handle_turn_request(_):
    if len(game.community_cards) != 3:
        emit('error', {'message': 'Flop must be dealt first.'})
        return
    game.deal_turn()
    emit('community_update', {'cards': [str(c) for c in game.community_cards]}, broadcast=True)


@socketio.on('request_river')
def handle_river_request(_):
    if len(game.community_cards) != 4:
        emit('error', {'message': 'Turn must be dealt first.'})
        return
    game.deal_river()
    emit('community_update', {'cards': [str(c) for c in game.community_cards]}, broadcast=True)


@socketio.on('reset_round')
def handle_reset_round(_):
    game.reset_round()
    print("Round has been reset.")

    # Notify all clients to clear hands and community cards
    for player in game.players.values():
        emit('hand', {'cards': []}, to=player.uuid)
    emit('community_update', {'cards': []}, broadcast=True)


if __name__ == "__main__":
    print("Starting poker server...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
    # I have no idea what "allow_unsafe_werkzeug=True" is but for some reason it was necessary for me to run -Jake





