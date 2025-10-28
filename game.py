# Adding comments for no limit texas hold-em poker rules
import Deck, Player, Pot, Card


# 0) game, dealer, deck, pot, and each player is created
class PokerGame:

    def __init__(self):
        self.players = {}
        self.deck = Deck.Deck()
        self.pot = Pot.Pot()
        self.community_cards = []
        self.turn_order = []  # player uuids in turn order
        self.current_turn_index = 0
        self.round_active = False

        # print("TEST",self.has_straight(
        #     [Card.Card("Hearts", "2"), Card.Card("Spades", "3"), Card.Card("Hearts", "4"), Card.Card("Hearts", "5"),
        #      Card.Card("Hearts", "6")]))


    # Add new player
    def add_player(self, name, uuid, seat_position, seat_position_flag, is_ready):
        self.players[uuid] = Player.Player(name, uuid, seat_position, seat_position_flag, is_ready)

    # Remove player
    def remove_player(self, uuid):
        if uuid in self.players:
            del self.players[uuid]

    # -----------------------------------Ready stuff--------------------------------

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
    #
    # # hand ranking stuff. needs to be organized, maybe into its own class? HandRanker class or something
    #
    # # return whether there is a straight within the hand and what the highest card of the straight is.
    # def has_straight(self, full_hand):
    #     has_straight = False
    #     # a straight requires 5 cards minimum
    #     if len(full_hand) < 5:
    #         return False, 0
    #     current_high_card_number = 0
    #     for card in full_hand:
    #         high_card = self.check_straight_offsets(card, full_hand)
    #         if high_card > current_high_card_number:
    #             has_straight = True
    #             current_high_card_number = high_card
    #     return has_straight, current_high_card_number
    #
    # def check_straight_offsets(self, card, full_hand):
    #     capture = 0
    #     for i in range(1, 5):
    #         if not self.value_in_full_hand(card.number + i, full_hand):
    #             return 0
    #         capture = i
    #     return card.number + capture
    #
    # def value_in_full_hand(self, card_number, full_hand):    # probably make static I guess
    #     for card in full_hand:
    #         if card.number == card_number:
    #             return True
    #     return False


    # def index_player_hand_rankings(self):
    #     return
    #
    # def has_royal_flush(self, full_hand):
    #     if Card.Card("Spades", "A") in full_hand \
    #             and Card.Card("Spades", "K") in full_hand \
    #             and Card.Card("Spades", "Q") in full_hand \
    #             and Card.Card("Spades", "J") in full_hand \
    #             and Card.Card("Spades", "10") in full_hand:
    #         return True
    #     if Card.Card("Clubs", "A") in full_hand \
    #             and Card.Card("Clubs", "K") in full_hand \
    #             and Card.Card("Clubs", "Q") in full_hand \
    #             and Card.Card("Clubs", "J") in full_hand \
    #             and Card.Card("Clubs", "10") in full_hand:
    #         return True
    #     if Card.Card("Hearts", "A") in full_hand \
    #             and Card.Card("Hearts", "K") in full_hand \
    #             and Card.Card("Hearts", "Q") in full_hand \
    #             and Card.Card("Hearts", "J") in full_hand \
    #             and Card.Card("Hearts", "10") in full_hand:
    #         return True
    #     if Card.Card("Diamonds", "A") in full_hand \
    #             and Card.Card("Diamonds", "K") in full_hand \
    #             and Card.Card("Diamonds", "Q") in full_hand \
    #             and Card.Card("Diamonds", "J") in full_hand \
    #             and Card.Card("Diamonds", "10") in full_hand:
    #         return True
    #     return False
    #
    # def has_straight_flush(self, full_hand):
    #     if Card.Card("Spades", "A") in full_hand \
    #             and Card.Card("Spades", "2") in full_hand \
    #             and Card.Card("Spades", "3") in full_hand \
    #             and Card.Card("Spades", "4") in full_hand \
    #             and Card.Card("Spades", "5") in full_hand:
    #         return True
    #     if Card.Card("Spades", "2") in full_hand \
    #             and Card.Card("Spades", "3") in full_hand \
    #             and Card.Card("Spades", "4") in full_hand \
    #             and Card.Card("Spades", "5") in full_hand \
    #             and Card.Card("Spades", "6") in full_hand:
    #         return True
    #     if Card.Card("Spades", "3") in full_hand \
    #             and Card.Card("Spades", "4") in full_hand \
    #             and Card.Card("Spades", "5") in full_hand \
    #             and Card.Card("Spades", "6") in full_hand \
    #             and Card.Card("Spades", "7") in full_hand:
    #         return True
    #     if Card.Card("Spades", "4") in full_hand \
    #             and Card.Card("Spades", "5") in full_hand \
    #             and Card.Card("Spades", "6") in full_hand \
    #             and Card.Card("Spades", "7") in full_hand \
    #             and Card.Card("Spades", "8") in full_hand:
    #         return True
    #     if Card.Card("Spades", "5") in full_hand \
    #             and Card.Card("Spades", "6") in full_hand \
    #             and Card.Card("Spades", "7") in full_hand \
    #             and Card.Card("Spades", "8") in full_hand \
    #             and Card.Card("Spades", "9") in full_hand:
    #         return True
    #     if Card.Card("Spades", "6") in full_hand \
    #             and Card.Card("Spades", "7") in full_hand \
    #             and Card.Card("Spades", "8") in full_hand \
    #             and Card.Card("Spades", "9") in full_hand \
    #             and Card.Card("Spades", "10") in full_hand:
    #         return True
    #     if Card.Card("Spades", "5") in full_hand \
    #             and Card.Card("Spades", "6") in full_hand \
    #             and Card.Card("Spades", "7") in full_hand \
    #             and Card.Card("Spades", "8") in full_hand \
    #             and Card.Card("Spades", "9") in full_hand:
    #         return True
    #
    # def has_four_of_a_kind(self, full_hand):
    #     return
    #
    # def has_full_house(self, full_hand):
    #     return
    #
    # def has_flush(self, full_hand):
    #     full_hand_suits = [card.suit for card in self.community_cards]
    #     full_hand_values = [card.value for card in self.community_cards]
    #     if full_hand_suits.count("Spades") >= 5:
    #         return 6, max(full_hand_values)

    # def rank_hand(self, player):
    #     suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    #     ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    #
    #     hand_rankings = {"royal_flush": 10,
    #                      "straight_flush": 9,
    #                      "four_of_a_kind": 8,
    #                      "full_house": 7,
    #                      "flush": 6,
    #                      "straight": 5,
    #                      "three_of_a_kind": 4,
    #                      "two_pair": 3,
    #                      "one_pair": 2,
    #                      "high_card": 1}
    #
    #
    #     full_hand = self.community_cards + player.hand
    #     full_hand_suits = [card.suit for card in (self.community_cards + player.hand)]
    #     full_hand_values = [card.value for card in (self.community_cards + player.hand)]
    #
    #     if len(full_hand) >= 5:
    #         if self.has_royal_flush(full_hand):
    #             return hand_rankings["royal_flush"]
    #     if len(full_hand) >= 4:
    #
    #     for card in full_hand_values:
    #         if full_hand_values.count(card) == 4:
    #             return hand_rankings["four_of_a_kind"], card
    #
    #         if full_hand_values.count(card) == 3:
    #             return hand_rankings["three_of_a_kind"], card
