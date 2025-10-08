from flask import Flask, request
from flask_socketio import SocketIO, emit
import random

from game import PokerGame

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") # allow external connections

# Single game instance
game = PokerGame()



"""Event Handlers"""


# When someone connects
@socketio.on('connect')
def handle_connect():
    print(f"Player connected: {request.sid}")
    emit('connected', {'message': 'Connected to server!'})


# When a player sets their name
@socketio.on('set_name')
def handle_set_name(data):
    name = data.get('name', 'Anonymous')
    uuid = request.sid
    game.add_player(name, uuid)
    print(f"Player joined: {name}")

