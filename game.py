# Adding comments for no limit texas hold-em poker rules
import Deck, Player, Pot


# 0) game, dealer, deck, pot, and each player is created
class PokerGame:

    def __init__(self):
        self.players = {}
        self.deck = Deck.Deck()
        self.pot = Pot.Pot()
        self.community_cards = []
        self.turn_order = [] # player uuids in turn order
        self.current_turn_index = 0
        self.round_active = False


    # Add new player
    def add_player(self, name, uuid, seat_position, seat_position_flag, is_ready):
        self.players[uuid] = Player.Player(name, uuid, seat_position, seat_position_flag, is_ready)


    # Remove player
    def remove_player(self, uuid):
        if uuid in self.players:
            del self.players[uuid]

    #-----------------------------------Ready stuff--------------------------------

    # Set a player's ready flag
    def set_ready(self, uuid, is_ready: bool):
        p = self.players.get(uuid)
        if not p:
            return None
        p.ready = bool(is_ready)
        return p.ready

    # Toggle a player's ready flag
    def toggle_ready(self, uuid):
        p = self.players.get(uuid)
        if not p:
            return None
        p.ready = not bool(getattr(p, 'ready', False))
        return p.ready

    # Set all player's ready flag to false
    def clear_all_ready(self):
        for p in self.players.values():
            p.ready = False

    # Return a boolean if all players are ready or not
    def all_ready(self):
        return len(self.players) > 0 and all(getattr(p, "ready", False) for p in self.players.values())


    # Return lobby info in a list of dictionaries
    def serialize_lobby(self):
        out = []
        for player in self.players.values():
            out.append({
                'uuid': player.uuid,
                'name': player.name,
                'ready': bool(getattr(player, 'ready', False)),
                'seat_position': getattr(player, 'seat_position', 0),
                'seat_position_flag': getattr(player, 'seat_position_flag', 0)
            })
        return out


    # Start a new round
    def start_round(self):
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0
        self.round_active = True
        self.community_cards = []

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


    # Discard one card (standard before flop/turn/river)
    def burn_card(self):
        _ = self.deck.deal(1)


    # Deal the flop (first three community cards)
    def deal_flop(self):
        if len(self.community_cards) > 0:
            return  # Flop already dealt
        self.burn_card()
        self.community_cards.extend(self.deck.deal(3))


    # Deal the turn (fourth community card).
    def deal_turn(self):

        if len(self.community_cards) != 3:
            return  # Flop must be dealt first
        self.burn_card()
        self.community_cards.extend(self.deck.deal(1))


    # Deal the river (fifth and final community card).
    def deal_river(self):
        if len(self.community_cards) != 4:
            return  # Turn must be dealt first
        self.burn_card()
        self.community_cards.extend(self.deck.deal(1))


    # End the round, clear states, and prepare for next hand.
    def reset_round(self):
        self.round_active = False
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.community_cards.clear()
        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0

        # Reset each player
        for player in self.players.values():
            player.reset_for_round()