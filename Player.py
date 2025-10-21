class Player:
    def __init__(self, name, uuid, seat_position, seat_position_flag, is_ready):
        self.name = name
        self.uuid = uuid
        self.money_count = 1000
        self.seat_position = seat_position
        self.hand = []  # List of Cards of length 2
        self.seat_position_flag = seat_position_flag  # one of Dealer, Big Blind, Little Blind
        self.folded = False
        self.current_bet = 0
        self.is_ready = is_ready

# returns a dictionary of the player data to pass around as json (cant pass regular python objects)
# we should keep our eye on this to make sure that the dictionary is
    # updated correctly (when we eventually access it in a more involved way)
    def to_dict(self):
        return {
            'name': self.name,
            'uuid': self.uuid,
            'money_count': self.money_count,
            'seat_position': self.seat_position,
            'hand': self.hand,
            'seat_position_flag': self.seat_position_flag,
            'folded': self.folded,
            'current_bet': self.current_bet
        }

    def receive_card(self, card):
        self.hand += card

    def make_bet(self, current_bet):
        self.money_count -= current_bet

    def receive_money(self, current_bet):
        self.money_count += current_bet

    def reset_for_round(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False

    @property
    def ready(self):
        return bool(self.is_ready)

    @ready.setter
    def ready(self, value):
        self.is_ready = bool(value)
