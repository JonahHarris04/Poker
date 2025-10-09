class Pot:
    def __init__(self):
        self.amount = 0

    def take_bet(self, bet_amount):
        self.amount += bet_amount

    def clear_pot(self):
        self.amount = 0

    def payout_single(self, player):
        player.money_count += self.amount
        self.clear_pot()

    def payout_split_pot(self, players):
        split_remainder = self.amount % len(players)
        split_amount = self.amount // len(players)
        if split_remainder == 0:
            for player in players:
                player.receive_money(split_amount)
            self.clear_pot()
        else:
            for player in players:
                player.receive_money(split_amount)
            self.amount = split_remainder
