# Adding comments for no limit texas hold-em poker rules
import Deck, Player, Card, Pot


# 0) game, dealer, deck, pot, and each player is created
class PokerGame:

    def __init__(self):
        self.players = {}
        self.deck = Deck.Deck()
        self.pot = Pot.Pot()
        self.turn_order = [] # player uuids in turn order
        self.current_turn_index = 0


    # Add new player
    def add_player(self, name, uuid, seat_position, seat_position_flag):
        self.players[uuid] = Player.Player(name, uuid, seat_position, seat_position_flag)


    # Remove player
    def remove_player(self, uuid):
        if uuid in self.players:
            del self.players[uuid]


    # Start a new round
    def start_round(self):
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0

        # Deal 2 cards to each player
        for player in self.players.values():
            player.reset_for_round()
            player.receive_card(self.deck.deal(2))


    # Get the current player
    def current_player(self):
        return self.players[self.turn_order[self.current_turn_index]]


    # Advance to the next players turn
    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        return self.current_player()

# app.py will handle all the game logic in coherence with socketio just so y'all know

