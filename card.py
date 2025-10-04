class Card:
    def __init__(self, unique_ID, suit, rank):
        self.unique_ID = unique_ID
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __rank__(self):
        return f"{self.rank}"
    
    def __suit__(self):
        return f"{self.suit}"
