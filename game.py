import Deck, Player, Pot

class PokerGame:

    def __init__(self):
        self.players = {}
        self.deck = Deck.Deck()
        self.pot = Pot.Pot()
        self.community_cards = []

        # Turn order
        self.turn_order = []
        self.current_turn_index = 0
        self.round_active = False

        # Betting state
        self.current_bet = 0
        self.street_contributions = {}
        self.minimum_raise = 0
        self.street = "preflop"  # preflop, flop, turn, river, showdown

    # -------------------- Player Management --------------------
    def add_player(self, name, uuid, seat_position, seat_position_flag, is_ready):
        self.players[uuid] = Player.Player(name, uuid, seat_position, seat_position_flag, is_ready)

    def remove_player(self, uuid):
        if uuid in self.players:
            del self.players[uuid]

    # -------------------- Ready System --------------------
    def set_ready(self, uuid, is_ready: bool):
        p = self.players.get(uuid)
        if not p:
            return None
        p.ready = bool(is_ready)
        return p.ready

    def toggle_ready(self, uuid):
        p = self.players.get(uuid)
        if not p:
            return None
        p.ready = not bool(getattr(p, 'ready', False))
        return p.ready

    def clear_all_ready(self):
        for p in self.players.values():
            p.ready = False

    def all_ready(self):
        return len(self.players) > 0 and all(getattr(p, "ready", False) for p in self.players.values())

    # -------------------- Round Management --------------------
    def start_round(self):
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.community_cards = []

        # Turn order: Player 1 always starts preflop
        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0
        self.round_active = True
        self.street = "preflop"

        # Betting state
        self.current_bet = 0
        self.minimum_raise = 10
        self.street_contributions = {uuid: 0 for uuid in self.players.keys()}

        # Deal 2 cards to each player
        for player in self.players.values():
            player.reset_for_round()
            player.receive_card(self.deck.deal(2))
            # Simple ante
            ante = 10
            player.chips -= ante
            self.pot.add_to_pot(ante)
            self.street_contributions[player.uuid] = ante
            player.acted_this_round = False

    def reset_round(self):
        self.round_active = False
        self.deck = Deck.Deck()
        self.deck.shuffle()
        self.pot.clear_pot()
        self.community_cards.clear()
        self.turn_order = list(self.players.keys())
        self.current_turn_index = 0
        for player in self.players.values():
            player.reset_for_round()
            player.acted_this_round = False

    # -------------------- Turn Management --------------------
    def current_player(self):
        return self.players[self.turn_order[self.current_turn_index]]

    def advance_turn(self):
        for _ in range(len(self.turn_order)):
            self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
            p = self.current_player()
            if not p.folded and p.chips > 0:
                return p
        return None

    # -------------------- Betting --------------------
    def apply_action(self, uuid, action, amount=0):
        p = self.players.get(uuid)
        if not p or p.folded or p.chips == 0:
            return False, "Invalid player state."

        # FOLD
        if action == "fold":
            p.folded = True
            p.acted_this_round = True
            return True, "Player folded."

        # CHECK
        if action == "check":
            if self.street_contributions[uuid] == self.current_bet:
                p.acted_this_round = True
                return True, "Checked."
            return False, "Cannot check facing a bet."

        # CALL
        if action == "call":
            call_amount = self.current_bet - self.street_contributions[uuid]
            bet_amount = min(call_amount, p.chips)
            p.chips -= bet_amount
            self.pot.add_to_pot(bet_amount)
            self.street_contributions[uuid] += bet_amount
            p.acted_this_round = True
            return True, "Called."

        # BET or RAISE
        if action in ["bet", "raise"]:
            if amount > p.chips:
                return False, "Not enough chips."
            if amount < 1:
                return False, "Must bet at least 1 chip."

            p.chips -= amount
            self.pot.add_to_pot(amount)
            self.street_contributions[uuid] += amount
            self.current_bet = max(self.current_bet, self.street_contributions[uuid])
            p.acted_this_round = True
            return True, "Bet/Raised."

        # ALL-IN
        if action == "allin":
            allin_amount = p.chips
            p.chips = 0
            self.pot.add_to_pot(allin_amount)
            self.street_contributions[uuid] += allin_amount
            self.current_bet = max(self.current_bet, self.street_contributions[uuid])
            p.acted_this_round = True
            return True, "All-in."

        return False, "Unknown action."

    def is_betting_round_complete(self):
        active = [p for p in self.players.values() if not p.folded and p.chips > 0]

        # Only 1 left -> showdown
        if sum(not p.folded for p in self.players.values()) <= 1:
            self.street = "showdown"
            return True

        # Everyone matched the bet or all-in
        return all(
            self.street_contributions[p.uuid] == self.current_bet or p.chips == 0
            for p in active
        )

    def move_to_next_street(self):
        # Reset contributions for new street
        for uuid in self.street_contributions:
            self.street_contributions[uuid] = 0
        self.current_bet = 0

        # Reset acted_this_round
        for p in self.players.values():
            p.acted_this_round = False

        # Move street
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

        # Set current player to first active
        self.current_turn_index = 0
        while self.current_player().folded or self.current_player().chips == 0:
            self.advance_turn()

    # -------------------- Available Actions --------------------
    def get_available_actions(self, uuid):
        p = self.players.get(uuid)
        if not p or p.folded:
            return []

        my_contribution = self.street_contributions[uuid]
        if p.chips == 0:
            return ["fold"]
        if self.current_bet == my_contribution:
            return ["check", "bet", "fold", "allin"]
        else:
            return ["call", "raise", "fold", "allin"]

    # -------------------- Serialize --------------------
    def serialize_game_state(self):
        return {
            "players": [
                {
                    "uuid": p.uuid,
                    "name": p.name,
                    "chips": p.chips,
                    "folded": p.folded,
                    "contribution": self.street_contributions.get(p.uuid, 0)
                } for p in self.players.values()
            ],
            "community_cards": [str(c) for c in self.community_cards],
            "pot": self.pot.amount,
            "current_bet": self.current_bet,
            "street": self.street,
            "current_turn": self.turn_order[self.current_turn_index] if self.turn_order else None
        }

    # -------------------- Dealing --------------------
    def burn_card(self):
        self.deck.deal(1)

    def deal_flop(self):
        if len(self.community_cards) == 0:
            self.burn_card()
            self.community_cards.extend(self.deck.deal(3))
            for p in self.players.values():
                p.acted_this_round = False

    def deal_turn(self):
        if len(self.community_cards) == 3:
            self.burn_card()
            self.community_cards.extend(self.deck.deal(1))
            for p in self.players.values():
                p.acted_this_round = False

    def deal_river(self):
        if len(self.community_cards) == 4:
            self.burn_card()
            self.community_cards.extend(self.deck.deal(1))
            for p in self.players.values():
                p.acted_this_round = False
