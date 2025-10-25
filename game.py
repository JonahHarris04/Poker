# Adding comments for no limit texas hold-em poker rules
import Deck, Player, Pot


# 0) game, dealer, deck, pot, and each player is created
class PokerGame:

    def __init__(self):
        self.players = {}
        self.deck = Deck.Deck()
        self.pot = Pot.Pot()
        self.community_cards = []

        # Turn order state
        self.turn_order = [] # player uuids in turn order
        self.current_turn_index = 0
        self.round_active = False

        # Betting state
        self.current_bet = 0   # Highest bet required to call
        self.street_contributions = {}
        self.minimum_raise = 0   # Enforce raise rules
        self.street = "preflop"   # preflop, flop, turn, river, showdown


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

    # Start a new round
    def start_round(self):
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.community_cards = []

        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0
        self.round_active = True
        self.street = "preflop"

        self.current_bet = 0
        self.minimum_raise = 10

        # Reset conrtibutions
        self.street_contributions = {uuid: 0 for uuid in self.players.keys()}

        # Deal 2 cards to each player
        for player in self.players.values():
            player.reset_for_round()
            player.receive_card(self.deck.deal(2))

            # Simple ante system: force each plater to pay 10 chips
            ante = 10
            player.chips -= ante
            self.pot.take_bet(ante)
            self.street_contributions[player.uuid] = ante


    # Get the current player
    def current_player(self):
        return self.players[self.turn_order[self.current_turn_index]]


    # Advance to the next players turn
    def advance_turn(self):
        # Skip folded or all-in players automatically
        for _ in range(len(self.turn_order)):
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            p = self.current_player()
            if not p.folded and p.chips > 0:
                return p
        return None  # No active players left -> showdown


# Betting logic which encapsulates dealing community cards as well

    def apply_action(self, uuid, action, amount=0):
        p = self.players.get(uuid)
        if not p or p.folded or p.chips == 0:
            return False, "Invalid player state."

        if action == "fold":
            p.folded = True
            return True, "Player folded."

        if action == "check":
            if self.street_contributions[uuid] == self.current_bet:
                return True, "Checked."
            return False, "Cannot check facing a bet."

        if action == "call":
            call_amount = self.current_bet - self.street_contributions[uuid]
            bet_amount = min(call_amount, p.chips)
            p.chips -= bet_amount
            self.pot.add_to_pot(bet_amount)
            self.street_contributions[uuid] += bet_amount
            return True, "Called."

        if action == "bet" or action == "raise":
            if amount < self.minimum_raise:
                return False, f"Minimum bet/raise: {self.minimum_raise}"

            if amount > p.chips:
                return False, "Not enough chips."

            # Update bet tracking
            p.chips -= amount
            self.pot.add_to_pot(amount)
            self.street_contributions[uuid] += amount
            self.minimum_raise = amount  # standard NL rule
            self.current_bet = self.street_contributions[uuid]

            return True, "Bet/Raised."

        if action == "allin":
            allin_amount = p.chips
            p.chips = 0
            self.pot.add_to_pot(allin_amount)
            self.street_contributions[uuid] += allin_amount
            self.current_bet = max(self.current_bet, self.street_contributions[uuid])

            return True, "All-in."

        return False, "Unknown action."

    def is_betting_round_complete(self):
        active = [p for p in self.players.values()
                  if not p.folded and p.chips >= 0]

        # If only 1 left, immediate showdown
        if sum(not p.folded for p in self.players.values()) <= 1:
            self.street = "showdown"
            return True

        # Everyone matched the bet (or all-in)
        return all(self.street_contributions[p.uuid] == self.current_bet or p.chips == 0
                   for p in active)

    def move_to_next_street(self):
        # Reset per-street contributions
        for uuid in self.street_contributions:
            self.street_contributions[uuid] = 0
        self.current_bet = 0

        if self.street == "preflop":
            self.burn_card()
            self.community_cards.extend(self.deck.deal(3))
            self.street = "flop"
        elif self.street == "flop":
            self.burn_card()
            self.community_cards.extend(self.deck.deal(1))
            self.street = "turn"
        elif self.street == "turn":
            self.burn_card()
            self.community_cards.extend(self.deck.deal(1))
            self.street = "river"
        elif self.street == "river":
            self.street = "showdown"

        # Skip folded/all-in players
        while not self.current_player() or self.current_player().folded or self.current_player().chips == 0:
            self.advance_turn()

    def burn_card(self):
        self.deck.deal(1)

    def get_available_actions(self, uuid):
        p = self.players.get(uuid)
        if not p or p.folded:
            return []

        my_contribution = self.street_contributions[uuid]

        if p.chips == 0:
            return ["fold"]  # stuck

        if self.current_bet == my_contribution:
            return ["check", "bet", "fold", "allin"]
        else:
            return ["call", "raise", "fold", "allin"]


    # Return lobby info in a list of dictionaries
    def serialize_game_state(self):
        return {
            "players": [{
                "uuid": p.uuid,
                "name": p.name,
                "chips": p.chips,
                "folded": p.folded,
                "contribution": self.street_contributions[p.uuid]
            } for p in self.players.values()],
            "community_cards": [str(c) for c in self.community_cards],
            "pot": self.pot.total,
            "current_bet": self.current_bet,
            "street": self.street,
            "current_turn": self.turn_order[self.current_turn_index]
        }