import random
import Card
class Deck:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.cards = [Card.Card(rank+suit, rank, suit) for suit in suits for rank in ranks] # rank + suit is placeholder unique id

    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal(self, num=1):
        dealt = [self.cards.pop() for _ in range(num)]
        return dealt
            
    def __len__(self):
        return len(self.cards)
        
