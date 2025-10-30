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
        self.last_aggressor = None # Last person to have set a new high

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
        self.last_aggressor = None

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
        self.last_aggressor = None
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

    # ------------------Game Logic Helpers--------------
    def reset_actions_after_aggression(self, aggressor_uuid):
        for player in self.players.values():
            player.acted_this_round = False
        self.players[aggressor_uuid].acted_this_round = True
        self.last_aggressor = aggressor_uuid

    def _first_active_index(self):
        # put turn on first non-folded player with chips >=0
        idx = 0
        if not self.turn_order:
            return 0
        while True:
            candidate = self.players[self.turn_order[idx]]
            if not candidate.folded:
                return idx
            idx = (idx + 1) % len(self.turn_order)

    # -------------------- Betting --------------------
    def apply_action(self, uuid, action, amount=0):
        p = self.players.get(uuid)
        if not p or p.folded or p.chips == 0:
            return False, "Invalid player state."

        my_contribution = self.street_contributions.get(uuid, 0)
        price_to_call = max(0, self.current_bet - my_contribution)

        # ---------------- FOLD ----------------
        if action == "fold":
            p.folded = True
            p.acted_this_round = True
            return True, f"{p.name} folded."

        # ---------------- CHECK ----------------
        if action == "check":
            if price_to_call > 0:
                return False, "Cannot check facing a bet."
            p.acted_this_round = True
            return True, f"{p.name} checked."

        # ---------------- CALL ----------------
        if action == "call":
            if price_to_call == 0:
                return False, "Nothing to call."
            to_put = min(price_to_call, p.chips)
            p.chips -= to_put
            self.pot.add_to_pot(to_put)
            self.street_contributions[uuid] = my_contribution + to_put
            p.acted_this_round = True
            return True, f"{p.name} called."

        # ---------------- BET ----------------
        if action == "bet":
            if self.current_bet > 0:
                return False, "Bet not allowed; use raise."
            if amount < self.minimum_raise:
                return False, f"Minimum bet is {self.minimum_raise}."
            if amount > p.chips:
                return False, "Not enough chips."
            p.chips -= amount
            self.pot.add_to_pot(amount)
            self.street_contributions[uuid] = my_contribution + amount
            self.current_bet = self.street_contributions[uuid]
            self.reset_actions_after_aggression(uuid)
            return True, f"{p.name} bet {amount}."

        # ---------------- RAISE ----------------
        if action == "raise":
            if price_to_call == 0:
                return False, "Cannot raise when no bet to call."
            raise_over_call = amount
            total_needed = price_to_call + raise_over_call
            if raise_over_call < self.minimum_raise and p.chips > price_to_call:
                return False, f"Minimum raise is {self.minimum_raise}."
            if total_needed > p.chips:
                return False, "Not enough chips."
            p.chips -= total_needed
            self.pot.add_to_pot(total_needed)
            self.street_contributions[uuid] = my_contribution + total_needed
            self.current_bet = self.street_contributions[uuid]
            self.reset_actions_after_aggression(uuid)
            return True, f"{p.name} raised by {raise_over_call}."

        # ---------------- ALL-IN ----------------
        if action == "allin":
            if p.chips == 0:
                return False, "Already all-in."
            to_put = p.chips
            p.chips = 0
            self.pot.add_to_pot(to_put)
            self.street_contributions[uuid] = my_contribution + to_put
            # If this all-in sets a new high, it's aggressive
            if self.street_contributions[uuid] > self.current_bet:
                self.current_bet = self.street_contributions[uuid]
                self.reset_actions_after_aggression(uuid)
                return True, f"{p.name} went all-in for {to_put}."
            else:
                p.acted_this_round = True
                return True, f"{p.name} called all-in."

        return False, "Unknown action."

    # Changed to fit with new logic
    def is_betting_round_complete(self):
        # Get active players (not folded, have chips)
        active = [p for p in self.players.values() if not p.folded and p.chips > 0]

        # If 0 or 1 active player, round is over
        if len(active) <= 1:
            self.street = "showdown"
            return True

        # Everyone has acted
        if not all(p.acted_this_round for p in active):
            return False

        # Everyone has matched the current bet (or is all-in)
        for p in active:
            contribution = self.street_contributions.get(p.uuid, 0)
            if contribution < self.current_bet:
                return False

        # All conditions met, round is complete
        return True

    def move_to_next_street(self):
        # Reset contributions for new street
        for uuid in self.street_contributions:
            self.street_contributions[uuid] = 0
        self.current_bet = 0
        self.last_aggressor = None

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
        self.current_turn_index = self._first_active_index()
        while self.current_player().folded or self.current_player().chips == 0:
            self.advance_turn()

    # -------------------- Available Actions --------------------
    def get_available_actions(self, uuid):
        p = self.players.get(uuid)
        if not p or p.folded:
            return []

        my_contribution = self.street_contributions.get(uuid, 0)
        price_to_call = max(0, self.current_bet - my_contribution)

        if p.chips == 0:
            return ["fold"]
        # If no one has bet price_to_call is zero
        if price_to_call == 0:
            return ["check", "bet", "allin", "fold"]
        else:
            actions = ["call", "allin", "fold"]
            # Hide raise if player can't do more than call
            if p.chips > price_to_call:
                actions.insert(1, "raise")
            return actions

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
