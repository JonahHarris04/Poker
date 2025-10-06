class Player:
    def __init__(self, uuid, money_count, seat_position, seat_position_flag):
        self.uuid = uuid
        self.money_count = money_count
        self.seat_position = seat_position
        self.hand = []  # List of Cards of length 2
        self.seat_position_flag = seat_position_flag  # one of Dealer, Big Blind, Little Blind

    def receive_card(self, card):
        self.hand += card

    def make_bet(self, amount):
        self.money_count -= amount

    def receive_money(self, amount):
        self.money_count += amount
