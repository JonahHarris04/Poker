import random
import card
class Deck:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.cards = [card.Card(rank+suit, rank, suit) for suit in suits for rank in ranks] # rank + suit is placeholder unique id

    def shuffle(self):
        random.shuffle(self.cards)
        
    def take_card_from_top(self):
        if self.cards:
            return self.cards.pop(0)
        else:
            return None
            
    def __len__(self):
        return len(self.cards)
        
