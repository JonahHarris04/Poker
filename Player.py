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



