import arcade

class Card(arcade.Sprite):
    def __init__(self, suit, value, scale = 1):

        self.suit = suit
        self.value = value

        # face up card
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.value}.png"

        # call parent
        super().__init__(self.image_file_name, scale, hit_box_algorithm="None")

    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __value__(self):
        return f"{self.value}"
    
    def __suit__(self):
        return f"{self.suit}"
