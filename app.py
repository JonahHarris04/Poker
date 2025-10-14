from flask import Flask, request
from flask_socketio import SocketIO, emit
import random

from game import PokerGame

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # allow external connections

# Single game instance
game = PokerGame()

# Event handlers

# When someone connects
@socketio.on('connect')
def handle_connect():
    print(f"Player connected: {request.sid}")
    emit('connected', {'message': 'Connected to server!'})


# When a player sets their name
@socketio.on('set_name')
def handle_set_name(data):
    name = data.get('player_name', 'Anonymous')
    uuid = request.sid
    game.add_player(name, uuid, seat_position=data.get('seat_position', 0), seat_position_flag=data.get('seat_position_flag', 0))

    print(f"Added player: {name}, SID={uuid}")
    print(f"Current players: {[p.name for p in game.players.values()]}")

    # Notify all players of player list
    emit('player_list', [p.name for p in game.players.values()], broadcast=True)


# Start a new round
@socketio.on('start_game')
def handle_start_game(data):
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


if __name__ == "__main__":
    print("Starting poker server...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)





